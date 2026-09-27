# Resumption after quota interruption

The first A expiry session completed. The first B expiry session passed its Java tests but was interrupted by a usage limit before final response or gate feedback. Four subsequent CLI sessions were rejected at startup by the same quota limit; no task tools ran. All original logs and results-before-resume.json are retained.

The user requested continuation. The usage tool now reports ordinary usage allowed. Resume the interrupted B session with no gate feedback yet; restart only the four sessions that never performed work, retaining their original prompts and assignments. No result is discarded. Frozen inputs and evaluator hashes are unchanged. Record resumption turns separately from gate correction turns, and exclude quota downtime from active session elapsed time. Interrupted-session token usage may be unavailable and must not be treated as zero total usage.
