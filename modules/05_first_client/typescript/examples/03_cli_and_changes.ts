/** A query CLI with no model dependency.
 * Run: npm exec tsx -- modules/05_first_client/typescript/examples/03_cli_and_changes.ts
 * Expected: matching release notes and the wiki index. Spec/capture: ../../README.md and scripts/tier1.py.
 */

import { main } from '../use_case/query.ts';
await main();
