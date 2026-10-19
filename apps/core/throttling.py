from rest_framework.throttling import ScopedRateThrottle


class AcceptedOnlyScopedThrottle(ScopedRateThrottle):
    """Scoped throttle that only counts *accepted* submissions.

    DRF's default throttles record every request, so a visitor who triggers validation errors
    (e.g. the "invalid payload" demo in the Backend Lab) would burn their quota and be locked out
    of the real contact form. Here `allow_request` only checks the history; the view calls
    `record()` once a submission has passed validation (honeypot hits included, so bots are limited too).
    """

    def allow_request(self, request, view):
        self.scope = getattr(view, self.scope_attr, None)
        if not self.scope:
            return True
        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)
        self.key = self.get_cache_key(request, view)
        if self.key is None:
            return True
        self.history = self.cache.get(self.key, [])
        self.now = self.timer()
        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()
        if len(self.history) >= self.num_requests:
            return self.throttle_failure()
        return True

    def record(self):
        if getattr(self, "key", None) is None:
            return
        self.history.insert(0, self.now)
        self.cache.set(self.key, self.history, self.duration)


def record_accepted(view):
    """Record an accepted submission on every AcceptedOnlyScopedThrottle active for this view."""
    for throttle in getattr(view, "_active_throttles", []):
        if isinstance(throttle, AcceptedOnlyScopedThrottle):
            throttle.record()
