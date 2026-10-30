# Filled security checklist

- [x] Synthetic fixtures only; no production identifiers or secrets.
- [x] Read paths and input sizes are bounded; error output omits credentials.
- [x] Mutation requires a separately reviewed decision; annotations alone do not authorize it.
- [x] HTTP deployment checks Host, Origin and token audience; local stdio inherits the invoking account's authority.
- [x] Retrieved text stays data. A source cannot grant itself tool permission.
- [x] Negative regression cases accompany positive acceptance.
- [ ] Real multi-user deployment: requires deployment-specific identity, shared storage, monitoring and recovery review. Out of this local capstone's acceptance scope.
