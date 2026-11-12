# Generative AI acknowledgment

GW University Policy on Generative AI.

**Tool.** Claude (Anthropic), model Opus 5, via Claude Code.

**How it is used.** Claude acts as a research assistant under direction. It
writes code, retrieves data from public databases, explains tools and methods,
and drafts prose. It does not choose the hypothesis, select which properties to
test, or decide what counts as a result.

**Decisions reserved to the author.** The research question and hypothesis, the
six pre-specified sequence properties, the choice to treat retained length as
the null model, the decision to report descriptive statistics with bootstrap
intervals rather than p-values, and acceptance or rejection of every proposed
analysis step.

**Per-phase record.** Each phase below records what was directed and what was
produced. Commit messages carry the same attribution.

## Proposal (Assignment 1, submitted 3 November 2026)

Directed Claude to read the assignment instructions, the rubric and the
author's research-interest documents, and to propose cellular rejuvenation
projects fitting the course. Three successive framings were rejected, including
one built on an evolutionary analysis and one whose central hypothesis the
author required verifying against the primary literature first. Claude then
read Hu et al. (2023) in full and confirmed the construct definitions and
efficiency data needed for a sequence-level analysis existed. The author
selected the hypothesis framing, the six properties, the title and the decision
to report preliminary results. Claude retrieved the supplementary archive,
extracted Tables S1 and S6, mapped eleven cloning primers onto the Sox17 coding
sequence, computed preliminary correlations, and drafted the proposal prose.

## Phase 0, data acquisition (12 November 2026)

None of the proposal-stage work was retained. The author directed a clean
rebuild so that every number in the final report regenerates from raw public
sources by one command, rather than being inherited from a chat session.

Claude wrote the repository skeleton, the pinned environment, the retrieval
code for NCBI RefSeq, UniProt and Europe PMC, the parser for the published
supplementary workbook, and the test suite. The author approved the phase plan,
the repository structure and the decision to pre-specify analysis parameters in
`config/analysis.yaml` before any outcome was examined.
