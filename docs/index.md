---
layout: single
title: "Cool Stuff"
subtitle: "The coolest stuff on the internet"
---

{% assign latest = site.data.coolstuff | last %}

### [{{ latest.name }}]({{ latest.url }})

{{ latest.description }}

[See all featured sites →](/archive/)

