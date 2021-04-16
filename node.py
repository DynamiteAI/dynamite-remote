import io
import os
import time
import json
import shutil
import socket
import tarfile
import logging
from typing import Dict, Optional
from sqlalchemy.exc import IntegrityError, NoResultFound

import const
import logger
import utilities
from database import db, models

AUTH_PATH = './dynamite_remote/auth'


class Node:

    def __init__(self, name: str, verbose: Optional[bool] = False, stdout: Optional[bool] = False):
        log_level = logging.INFO
        if verbose:
            log_level = logging.DEBUG
        self.logger = logger.get_logger('dynamite_remote', stdout=stdout, level=log_level)
        self.name = name
        self.key_path = f'{AUTH_PATH}/{self.name}'

    @classmethod
    def create_from_host_str(cls, hoststr: str, verbose: Optional[bool] = False, stdout: Optional[bool] = False):
        if ':' in hoststr:
            host, port = hoststr.split(':')
            port = int(port)
        else:
            host = hoststr
            port = 22
        metadata = db.db_session.query(models.Node). \
            filter(models.Node.host == host and models.Node.port == port). \
            one()
        return cls(metadata.name, verbose, stdout)

    def installed(self):
        return bool(self.get_metadata())

    def get_metadata(self) -> Optional[models.Node]:
        try:
            metadata = db.db_session.query(models.Node).\
                filter(models.Node.name == self.name).\
                one()
        except NoResultFound:
            return None
        return metadata

    def install(self, host: str, port: int, description: str, constants: Optional[Dict] = None):

        def generate_keypair():
            tmp_key_root = '/tmp/dynamite-remote/keys/'
            tmp_priv_key_path = f'{tmp_key_root}/{self.name}'
            tmp_key_file_path = f'{AUTH_PATH}/{self.name}'
            shutil.rmtree(tmp_key_root, ignore_errors=True)
            ret, stdout, stderr = utilities.create_new_remote_keypair(node_name=self.name)
            if ret != 0:
                self.logger.error(f'An [error {ret}] occurred while attempting to generate keypair via ssh-keygen: '
                                  f'{stdout}; {stderr}')
                exit(1)
            utilities.makedirs(AUTH_PATH)
            utilities.set_permissions_of_file(AUTH_PATH, 700)
            with open(tmp_priv_key_path, 'r') as key_in:
                with open(tmp_key_file_path, 'w') as key_out:
                    key_out.write(key_in.read())
            utilities.set_permissions_of_file(tmp_key_file_path, 600)

        def create_auth_package():
            tmp_pub_key_path = f'/tmp/dynamite-remote/keys/{self.name}.pub'
            metadata_info = dict(
                node_name=self.name,
                hostname=socket.gethostname(),
                dynamite_remote_version=const.VERSION
            )
            metadata_f = io.BytesIO()
            data = json.dumps(metadata_info).encode('utf-8')
            metadata_f.write(data)
            metadata_f.seek(0)
            with tarfile.open(self.name + '.tar.gz', 'w:gz') as tar_out:
                tar_out.add(
                    tmp_pub_key_path, arcname='key.pub'
                )
                tarinfo = tarfile.TarInfo('metadata.json')
                tarinfo.size = len(data)
                tar_out.addfile(tarinfo, metadata_f)
        self.logger.info('Initializing Database.')
        db.init_db()
        new_node = models.Node(
            name=self.name,
            host=host,
            port=port,
            description=description
        )
        db.db_session.add(new_node)
        try:
            db.db_session.commit()
        except IntegrityError as e:
            if 'UNIQUE' in str(e):
                self.logger.error('A node with this name or host has already been installed. '
                                  'Please uninstall first then try again.')
                exit(1)
        self.logger.debug(f'Node entry created: {self.name, host, description}')
        generate_keypair()
        self.logger.debug(f'{self.name} private key installed to {AUTH_PATH}')
        self.logger.info(f'{self.name} ({host}) node installed.')
        create_auth_package()
        self.logger.info(f'Authentication package generated successfully. Copy \'{self.name}.tar.gz\' to {host} and '
                         f'install via \'sudo dynamite remote install {self.name}.tar.gz\'.')
        return self

    def invoke_command(self, *dynamite_arguments):
        metadata = self.get_metadata()
        time.sleep(1)
        utilities.execute_dynamite_command_on_remote_host(metadata.host, metadata.port, self.key_path,
                                                          *dynamite_arguments)


def install_node_from_directory(path: str, verbose: Optional[bool] = False, stdout: Optional[bool] = False) -> Node:
    metadata_fp = f'{path}/metadata.json'
    with open(metadata_fp, 'r') as metadata_in:
        metadata_data = json.load(metadata_in)
        name = metadata_data['name']
        host = metadata_data['host']
        port = metadata_data['port']
        description = metadata_data['description']
    return Node(
        name=name,
        stdout=stdout,
        verbose=verbose
    ).install(
        host=host,
        port=port,
        description=description
    )


def install_node_from_tarball(path: str, verbose: Optional[bool] = False, stdout: Optional[bool] = False) -> Node:
    tmp_archive_dir = f'/tmp/dynamite-remote/{int(time.time())}'
    utilities.makedirs(tmp_archive_dir)
    utilities.extract_archive(path, tmp_archive_dir)
    return install_node_from_directory(tmp_archive_dir, verbose=verbose, stdout=stdout)
