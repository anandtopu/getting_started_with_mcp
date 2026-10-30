# Audit findings and verified repairs

| Finding | Reproduction against the isolated fixture | Impact | Repair and regression |
|---|---|---|---|
| Missing object authorization | read_record(name="private") | Leaks fixed FAKE salary | Deny any non-public key before reading; assert tool error |
| Missing confirmation | publish_bulletin(text="Unreviewed") | Changes an ephemeral bulletin without review | Require confirmed boolean; assert no unapproved success |
| Unbounded text | Send a 201-character bulletin | Excessive model/context payload | Enforce 1–200 characters in repaired implementation |

The fixture intentionally has no file or network capability, so these reproductions cannot access real confidential data. The repair preserves legitimate public reads and reviewed writes. Audit fields must omit bodies and credentials.
