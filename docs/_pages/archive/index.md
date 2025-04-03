---
layout: archive
title: Archive
permalink: /archive/
---

A list of all the cool stuff we've featured:

<ul>
{% assign latest = site.data.coolstuff | last %}
{% for site in site.data.coolstuff reversed %}
  {% unless site.url == latest.url %}
    <li><strong>{{ site.date }}:</strong> <a href="{{ site.url }}">{{ site.name }}</a>
      <br>{{ site.description }}</li>
  {% endunless %}
{% endfor %}
</ul>
