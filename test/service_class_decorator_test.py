#coding: utf-8
#created at 17-3-7 18:30

#from tasks import services
from tasks.service import Service, register_service


@register_service
class MockService(Service):
    name = "mockservice"


print Service.services
mockservice = Service.get_service("mockservice")
print mockservice.get_message_id