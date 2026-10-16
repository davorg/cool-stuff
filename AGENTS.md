# Guide for AI agents

## Purpose and architecture

This repository powers **Cool Stuff**, a website at `https://cool-stuff.co.uk`
that features interesting, creative, or fun websites. It demonstrates using
ChatGPT to curate a daily recommendation. `README.md` gives the project overview
and links to its introductory blog post.

The current site is a static Jekyll site hosted on GitHub Pages. A scheduled
GitHub Action runs a Perl script, which asks OpenAI for one recommendation and
appends it to a versioned YAML file. Jekyll reads that file to render the home
page, archive, and RSS feed. There is no application server or database.

The repository also preserves three older static websites under the same domain;
they are separate from the recommendation system.

## Repository map

| Path | Role |
| --- | --- |
| `bin/fetch_cool_site` | Perl program that requests and stores a recommendation. |
| `.github/workflows/update-coolstuff.yml` | Daily/manual update workflow; installs dependencies, runs Perl, commits and pushes data changes. |
| `docs/` | Jekyll source and static assets, rather than general project documentation. |
| `docs/_data/coolstuff.yml` | Authoritative list of featured websites, in append order. |
| `docs/index.md` | Home page: displays the final YAML entry and links to the archive. |
| `docs/_pages/archive/index.md` | `/archive/`: entries in reverse order, excluding entries whose URL matches the home-page entry. |
| `docs/feed.xml` | Custom RSS feed containing all entries in reverse order. |
| `docs/_config.yml` | Site metadata, theme, plugins, page collection, sitemap defaults, and analytics. |
| `docs/CNAME` | Custom domain, `cool-stuff.co.uk`. |
| `docs/robots.txt` | Allows crawling. |
| `docs/BevFox/` | Historical Bev Fox & the Shy People site, including CSS, images, and WAV/AU/RealAudio files. |
| `docs/Cartland/` | Historical Barbara Cartland pages, articles, CSS, and images. |
| `docs/LabourWatch/` | Historical political commentary, CSS, and images. |
| `humans.txt` | Authorship and technology credits at the repository root. |

## How a daily update works

1. GitHub Actions runs at `0 2 * * *` (02:00 UTC), or via
   `workflow_dispatch`. It checks out the repository on `ubuntu-latest`.
2. The workflow installs `cpanminus`, then the CPAN modules
   `OpenAPI::Client::OpenAI`, `YAML`, `JSON::MaybeXS`, and `Data::Printer`.
3. It exposes the repository secret `OPENAI_API_KEY` as an environment variable
   and runs `perl bin/fetch_cool_site` from the repository root.
4. The script requires the key, loads `docs/_data/coolstuff.yml`, and puts all
   previous entry names into a prompt asking for one new site, returned as JSON.
5. It calls `createChatCompletion` with model `gpt-6-luna`,
   `reasoning_effort => 'none'`, and temperature `1.0`. Reasoning is disabled to
   keep this short curation task inexpensive and allow the temperature setting.
   The code defines a JSON schema for `name`, `url`, and `description`, and passes
   `response_format` alongside `body` in the client call. Verify the client API
   before changing this request structure; the presence of a schema does not
   establish that responses are validated locally.
6. API errors print the response JSON and exit with status 1. Otherwise, the
   script takes the first choice's message content, encodes it as UTF-8, and
   decodes the JSON. Invalid JSON produces a warning and terminates the run.
7. It adds `date` using `localtime->ymd`. If no existing entry has the exact same
   URL string, it appends the entry and rewrites the YAML with `YAML::DumpFile`.
   An exact duplicate URL causes no write, with no retry for another suggestion.
8. The workflow stages only the YAML file, commits it as `Add new cool site` if
   changed, and pushes. Site publishing is handled separately by GitHub Pages;
   this workflow does not build or deploy Jekyll itself. Pages settings are not
   defined in the checked-in workflow.

The prompt asks for working URLs and avoidance of previously featured names.
The script does not fetch URLs to check availability, validate the decoded
object against the schema, or normalize URLs before duplicate detection. A
successful run therefore need not produce a new entry or guarantee a valid site.

## Data contract and rendering

The YAML document is an array of mappings with these fields:

```yaml
- date: 2026-10-16
  description: A paragraph explaining why the website is interesting.
  name: Example website
  url: https://example.org/
```

Preserve append order: the home page uses Liquid's `last`, and the archive and
feed reverse the array. They do not sort by date. Date values use `YYYY-MM-DD`;
there is no rule enforcing one entry per date. Keep existing history when
making targeted edits and avoid unnecessary reformatting of this large file.

The home page and archive output descriptions through Markdown/HTML processing;
the RSS description explicitly uses `xml_escape`. The feed uses each URL as its
GUID and formats the date using `date_to_rfc822`.

The site uses remote theme `mmistakes/minimal-mistakes@4.26.1`. Configured plugins
are `jekyll-feed`, `jekyll-seo-tag`, `jekyll-include-cache`, `jekyll-data`, and
`jekyll-sitemap`. The archive belongs to the `pages` collection. Sitemap inclusion
defaults to false, with explicit opt-in on the home and archive pages. Google
Analytics is configured in Jekyll and embedded directly in historical HTML.

## Working locally and validating changes

Run commands from the repository root: the Perl script resolves its YAML path
relative to the current working directory. Use a recent Perl that supports
`experimental 'try'` and `builtin`; the repository does not declare or pin a
minimum version. In addition to the CPAN modules installed by the workflow, the
script uses core modules `Time::Piece` and `Encode`.

There is no checked-in `cpanfile`, `Gemfile`, dependency lockfile, automated test
suite, or Jekyll build workflow. The update workflow is the dependency reference
for Perl. If modules are missing, install its four CPAN dependencies into your
normal local Perl environment.

Offline checks, when Perl dependencies are installed:

```sh
perl -c bin/fetch_cool_site
perl -MYAML=LoadFile -e '
  my $entries = LoadFile("docs/_data/coolstuff.yml");
  die "Expected an array\n" unless ref($entries) eq "ARRAY";
  for my $entry (@$entries) {
    die "Expected a mapping\n" unless ref($entry) eq "HASH";
    for my $key (qw(date name url description)) {
      die "Missing $key in " . ($entry->{name} // "unnamed entry") . "\n"
        unless defined $entry->{$key};
    }
  }
  print scalar(@$entries), " entries parsed\n";
'
git diff --check
```

For template or configuration changes, if a compatible Jekyll environment with
the remote-theme support and configured plugins is available, build outside the
source tree and inspect the generated home page, archive, RSS, and affected
historical pages:

```sh
jekyll build --source docs --destination /tmp/cool-stuff-site
```

The remote theme may require network access. The repository does not supply a
reproducible Ruby dependency setup; report any environment-related inability to
build instead of claiming the site was verified.

Live generator commands require `OPENAI_API_KEY` in the environment:

```sh
perl bin/fetch_cool_site debug
perl bin/fetch_cool_site
```

The first command still makes a paid network request, then prints the raw model
content and exits before JSON decoding, dating, duplicate checking, or writing.
It is not an offline test. The second command can rewrite the production data
file. Use these only when a live generation is part of the task, and never put
the API key into source, documentation, or logs.

## Change guidance

- Change curation and persistence in `bin/fetch_cool_site`; change scheduling and
  CI dependencies in `.github/workflows/update-coolstuff.yml`.
- Change the data file for individual recommendations and the Liquid templates
  for display behavior. A recommendation edit can affect all three views.
- Preserve the historical sites' case-sensitive filenames, public paths,
  relative asset links, and media files. They are static artifacts, not generated
  recommendation content. Their old CGI form and guestbook targets have no
  implementation here and cannot run on static GitHub Pages hosting.
- Keep changes scoped to the request. Do not modernize the historical sites,
  change the generation model, or rewrite the existing data incidentally while
  working elsewhere.
- Report which checks ran and distinguish offline validation from live API or
  GitHub Pages verification.
