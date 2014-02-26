pboots/pxelinux
---------------

pboots/pxelinux is an Django application which enables you to serve PXELINUX
configuration files dynamically based on the IP-address of the client and the
current time.
It is was build with scalability in mind. Thousands of clients with hundreds of
different configurations should be perfectly fine with an Raspberry Pi as
Server.

### configuration

See my [pboots repo](/zvyn/pboots/) for an working Django setup with sample
configurations for nginx and uwsgi.
The boot configuration is done with the Django admin module based on the
`models.py` and `admin.py` files. So here is a minimal step-by-step how-to:

1. Configure your installation according to the [README.md from
   pboots](/zvyn/pboots/README.md)
2. Go to `https://example.com/cfg`.
3. Click `add Item`.
4. Fill out the form.
5. Repeat 3 and 4 for `menu` and `machine set`.
6. Boot the client.
7. ???
8. Have fun.
