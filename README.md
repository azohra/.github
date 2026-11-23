# Workflows

Reusable GitHub Actions workflows for my repositories. Everything here is public, because a public repository can only call a public workflow.

A repository calls one by naming it in a job and follows `main`, so a fix here reaches every caller without a pull request in each:

```yaml
jobs:
  title:
    uses: azohra/.github/.github/workflows/title.yml@main
```

`title.yml` checks that a pull request title is a Conventional Commit line and labels the pull request with the type's label from the change table. The check reports as `title / Conventional PR title`, the name the fleet's rulesets require; the label job is separate so it can never block a merge. Callers grant it `pull-requests: write`. Both jobs run on `ubuntu-latest` unless the calling repository or its organization sets the `SHARED_WORKFLOW_RUNNER` variable to another runner label, such as an organization's larger runners. The labeler explicitly reads `azohra/.github:release-drafter.yml@main`, so callers in other accounts use the same change table.

`cliff.toml` is the changelog configuration every repository's `mise run changelog` fetches from this repository's main. It files each Conventional type where the commit reference in the skills says it goes, and `mise run check` here proves the release-draft configuration files them the same way.

Dependabot uses `ci(deps)` for Actions, `fix(deps)` for runtime or unclassified
dependencies, and `build(deps-dev)` for development dependencies where supported.
Runtime refreshes are deliberately eligible for patch releases; routine updates
keep their generated type. Separate production and development groups preserve
that classification. Dependabot cannot infer breaking changes to a consuming
application; add breaking markers when its supported contract changes. The
existing title, label and release rules implement these defaults.

`release-draft.yml` keeps one draft release listing what is unreleased, grouped by the labels the title check wrote. It titles releases `<repository> v<version>`, reads its rules from `release-drafter.yml` here, and takes `pre_v1: true` for a repository whose breaking changes should advance the minor version.

`dependabot-merge.yml` turns on GitHub's auto-merge, squashing, for a patch or minor Dependabot update; a major waits for a person. The required checks still gate the merge. It runs on `pull_request_target` and checks nothing out, reads the update's type from Dependabot's commit, and acts as the Azohra Bosun app with a token limited to the calling repository's contents and pull requests, so the merge starts the workflows on `main` that a merge by `GITHUB_TOKEN` would not. The caller passes `BOSUN_PRIVATE_KEY`, which with the `BOSUN_CLIENT_ID` variable lives in the calling repository's `automation` environment, deployable from `main` only, because the key reaches every repository Bosun is installed in:

```yaml
name: Dependabot auto-merge

on:
  pull_request_target:
    types:
      - opened
      - reopened
      - synchronize

permissions:
  contents: read
  pull-requests: read

jobs:
  merge:
    uses: azohra/.github/.github/workflows/dependabot-merge.yml@main
    secrets:
      BOSUN_PRIVATE_KEY: ${{ secrets.BOSUN_PRIVATE_KEY }}
```

`shared-workflows.json` declares the reference, pull request events and
permissions of the two callers that have one fixed shape, the title caller and
the Dependabot auto-merge caller, for policy audits. Reference drift is
reported by the policy audit; there is no additional pull request check. The
native required title result and the independent label job keep their
existing roles.
