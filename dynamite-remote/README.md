# dynamite-remote

```
$ dynamite-remote -h

usage: Dynamite Remote [-h] {execute,create} ...

Remotely manage DynamiteNSM nodes across your network environments.

positional arguments:
  {execute,create}

optional arguments:
  -h, --help        show this help message and exit

```
## Install

```
$ dynamite-remote create -h

usage: Dynamite Remote create [-h] --name NAME --host HOST [--port PORT] [--description DESCRIPTION]

optional arguments:
  -h, --help            show this help message and exit
  --name NAME           A friendly name for the remote node.
  --host HOST           A host or IP address of the remote node you will be connecting to.
  --port PORT           The corresponding SSH port to use.
  --description DESCRIPTION
                        A description of this node (E.G web-server environment sensor)

```
## Execute 

```
$ dynamite-remote execute -h

usage: Dynamite Remote execute [-h] remote command [command ...]

positional arguments:
  remote      The name of the node or node group to execute the command against.
  command     The command to run on the remote node (E.G 'elasticsearch process status').

optional arguments:
  -h, --help  show this help message and exit

```
