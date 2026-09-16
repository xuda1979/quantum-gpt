# DEPLOY-INTEGRITY — role card
Authority: verify tree == bundle == box (per-file sha256 from the MANIFEST list, never globs);
token-scan every member for box-breaking constructs (zip strict=, X|Y, match) before deploy;
refuse any deploy with an active lock on a member or missing evidence. Deploy-first protocol:
pin -> deploy -> sha-verify on box -> then anything fires.
