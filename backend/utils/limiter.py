"""
Shared rate-limiter instance (slowapi / limits) used by main.py and by any
route module that needs to throttle an endpoint. Kept in its own module so
route files can import it without creating a circular import with main.py.
"""

try:
	from slowapi import Limiter
except ImportError:
	class Limiter:
		def __init__(self, *args, **kwargs):
			self.args = args
			self.kwargs = kwargs

		def limit(self, *args, **kwargs):
			def decorator(func):
				return func

			return decorator


def get_remote_address(request):
	client = getattr(request, "client", None)
	return getattr(client, "host", "unknown")


limiter = Limiter(key_func=get_remote_address)