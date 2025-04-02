---
layout: archive
title: Archive
permalink: /archive/
---

A list of all the cool stuff we've featured:

<ul>
{% for site in site.data.coolstuff reversed %}
  <li><strong>{{ site.date }}:</strong> <a href="{{ site.url }}">{{ site.name }}</a><br>
    {{ site.description }}</li>
{% endfor %}
</ul>
