# INSTALLATION

For an initial deployment:

1. Edit the `local` section of the `hosts` file and add the IP address of your server / vm

2. Run the `provision` play:

```
$ ansible-playbook playbook.yml -i hosts -t provision -l local --ask-vault-pass
```

Where `local` is the the target environment.

# Deploying updates

```
$ ansible-playbook playbook.yml -i hosts -t update -l local --ask-vault-pass
```

Where `local` is the the target environment.

# Running the tests

You can run the tests with:

```
$ tox
```
