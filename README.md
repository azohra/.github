# Workflows

Reusable GitHub Actions workflows for my repositories. Everything here is public, because a public repository can only call a public workflow.

A repository calls one by naming it in a job and follows `main`, so a fix here reaches every caller without a pull request in each:

```yaml
jobs:
  title:
    uses: azohra/.github/.github/workflows/title.yml@main
```

`title.yml` checks that a pull request title is a Conventional Commit line and labels the pull request with the type's label from the change table. The check reports as `title / Conventional PR title`, the name the fleet's rulesets require; the label job is separate so it can never block a merge. Callers grant it `pull-requests: write`.

`cliff.toml` is the changelog configuration every repository's `mise run changelog` fetches from this repository's main. It files each Conventional type where the commit reference in the skills says it goes, and `mise run check` here proves the release-draft configuration files them the same way.

`release-draft.yml` keeps one draft release listing what is unreleased, grouped by the labels the title check wrote. It titles releases `<repository> v<version>`, reads its rules from `release-drafter.yml` here, and takes `pre_v1: true` for a repository whose breaking changes should advance the minor version.
