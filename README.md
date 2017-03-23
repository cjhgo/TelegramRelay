
TelegramRelay

A telegram message broker server based on tornado, which includes 
a crawler to fetch title and redis db to store result.
Set your telegram token and config your db, collection name, 
you can just launch it up.
You can customize your message protocol and install it in the servic
directory under the task folder, which can be done with the usage of
register service decorator.
The project to display the messages is under another project based on flask, whose 
repoistory address is [www](https://github.com/cjhgo/www)

remark
this is a project  for personal usage.
the key and token had been outdated after the release 
to the public repository.