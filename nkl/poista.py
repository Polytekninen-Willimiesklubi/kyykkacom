from pymemcache.client.base import Client

# Use pymemcache as the client. Django settings already use
# `PyMemcacheCache` so this keeps the memcache client consistent.

mc = Client(("127.0.0.1", 11211))

# Store a string value (pymemcache returns bytes for gets)
mc.set(b"some_key", b"Some value")
value = mc.get(b"some_key")
if isinstance(value, bytes):
	value = value.decode()

# Set and delete
mc.set(b"another_key", b"3")
mc.delete(b"another_key")

# Increment/decrement: values must be bytes/strings that represent integers
mc.set(b"key", b"1")
mc.incr(b"key", 1)
mc.decr(b"key", 1)

print(mc.get(b"key"))
