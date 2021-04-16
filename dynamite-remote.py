import os
import argparse
import node

import logger


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Dynamite Remote', description='Remotely manage DynamiteNSM nodes across your '
                                                                    'network environments.')
    subparsers = parser.add_subparsers()
    execute_parser = subparsers.add_parser('execute')
    create_node_parser = subparsers.add_parser('create')

    # Execute Command
    execute_parser.set_defaults(action='execute')
    execute_parser.add_argument(
        'remote', help='The name of the node or node group to execute the command against.'
    )
    execute_parser.add_argument(
        'command', help='The command to run on the remote node (E.G \'elasticsearch process status\').', nargs='+',
        type=str
    )

    # Setup From archive
    create_node_parser.set_defaults(action='create')
    create_node_parser.add_argument(
        '--name', type=str, required=True, help='A friendly name for the remote node.',
    )
    create_node_parser.add_argument(
        '--host', type=str, required=True, help='A host or IP address of the remote node you will be connecting to.',
    )
    create_node_parser.add_argument(
        '--port', type=int, required=False, help='The corresponding SSH port to use.', default=22
    )
    create_node_parser.add_argument(
        '--description', type=str, required=False, help='A description of this node (E.G web-server environment sensor)',
        default='Remote node'
    )

    args = parser.parse_args()
    if args.action == 'execute':
        remote_node = node.Node(args.remote, stdout=True)
        if not remote_node.installed():
            remote_node = node.Node.create_from_host_str(args.remote, stdout=True)
        if not remote_node.installed():
            exit(1)
        remote_node.invoke_command(*args.command)

    elif args.action == 'create':
        node.Node(
            name=args.name,
            stdout=True,
            verbose=True
        ).install(
            host=args.host,
            port=args.port,
            description=args.description,
        )


