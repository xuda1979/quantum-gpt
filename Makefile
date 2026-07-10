.PHONY: hermes chat

ifeq ($(filter hermes,$(MAKECMDGOALS)),hermes)
HERMES_EXTRA_GOALS := $(filter-out hermes,$(MAKECMDGOALS))
HERMES_PROFILE ?= $(word 1,$(HERMES_EXTRA_GOALS))
HERMES_COMMAND ?= $(word 2,$(HERMES_EXTRA_GOALS))
HERMES_MODEL ?= $(word 3,$(HERMES_EXTRA_GOALS))

ifneq ($(words $(HERMES_EXTRA_GOALS)),0)
$(eval $(HERMES_EXTRA_GOALS):;@:)
endif
endif

hermes:
	@if [ -z "$(HERMES_PROFILE)" ]; then \
		echo "Usage: make hermes <profile> [chat] [model]"; \
		echo "Example: make hermes yunwu-claude chat claude-opus-4-7"; \
		echo "Note: GNU make consumes '-p' itself, so use positional args or HERMES_PROFILE=/HERMES_MODEL= vars here."; \
		exit 2; \
	fi
	@cmd=chat; \
	if [ -n "$(HERMES_COMMAND)" ]; then cmd="$(HERMES_COMMAND)"; fi; \
	args=""; \
	if [ -n "$(HERMES_MODEL)" ]; then args="$$args -m $(HERMES_MODEL)"; fi; \
	exec hermes -p "$(HERMES_PROFILE)" "$$cmd" $$args

# ── Trustable evaluation subsystem ──────────────────────────────────────────
# See evals/trust/README.md for the full design. These targets wrap the
# most common workflows. The harness must pass its own self-tests before
# any result is trusted.

.PHONY: trust-test trust-suite-init

trust-test:
	@PYTHONPATH=. python3 -m pytest evals/trust/tests/ -v

trust-suite-init:
	@PYTHONPATH=. python3 -m evals.trust.cli.main suite-init \
		--tasks evals/tasks/quantum \
		--out evals/trust/suite.lock.json \
		--notes "iter-3 quantum holdout"
