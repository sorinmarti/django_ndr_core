Language

{variable}
{nested.variable}
{variable|filter}
{variable|filter1|filter2}
{variable|filter1:arg1,arg2|filter2}
{variable|filter1:option=True|filter2|filter3}
{variable|filter1:arg1,arg2|filter2:option=True|filter3}

Filters

upper, lower, capitalize, title
takes: string
returns: string

pill/badge
takes: string, dict

fieldify
takes: string, dict

img
filters: iiif_resize 0-100

bool