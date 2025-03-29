import memcache

mc = memcache.Client(["127.0.0.1:11211"], debug=0)
mc.set("some_key", "Some value")
value = mc.get("some_key")
mc.set("another_key", 3)
mc.delete("another_key")
mc.set("key", 1)  # note that the key used for incr/decr must be a string.
mc.incr("key")
mc.decr("key")


print(mc.get("key"))
