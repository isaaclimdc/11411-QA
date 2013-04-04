#!/usr/local/bin/python
import re

def extractEntity(content):
  entity = content.split('\n', 1)[0]
  replace_regex = re.compile('\(programming\ language\)|language|\(film\)', re.IGNORECASE)

  entity = replace_regex.sub('', entity)
  return entity.strip()
