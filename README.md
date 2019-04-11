pboots/pxelinux
---------------

A Django app serving PXELINUX configuration based on time and client IP.

Use this app to manage the boot-behaviour of PXE clients (e.g. PCs in a computer
lab) where the desired OS depends on time and network address of the client.

### Configuration

[pboots](https://github.com/zvyn/pboots/) contains this repo as submodule.
Go there for a Django project with nginx and uwsgi sample configuration files.

### Usage

To specify which client boots what and when:

1. Go to `/cfg`, click `add Item`, fill out the form and save.
2. Repeat the previous step with `add Menu` and `add Machine Set`.
3. Boot the client(s).

### Scalabilety

Thousands of clients with hundreds of different configurations should be
perfectly fine with a Raspberry Pi as server. Keep in mind that this app serves
PXE configuration files only, not the OS images wich can (and typically should)
come form another machine.
