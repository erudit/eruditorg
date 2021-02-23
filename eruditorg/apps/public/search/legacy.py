""" Functions that deal with the quirks of the legacy search engine """
import functools


def group_results_by_field_correspondence(aggregations, field, correspondences):
    """ Group results count by field correspondence

    Sometimes in the indexed documents, some fields have different values
    when that shouldn't be the case. For example, in the field_values
    fields, we sometimes have "Compte rendu" and sometimes "Compterendu".
    This is clearly due to a typo and they should be grouped together.

    This function groups the results in the aggregations dictionary and
    deletes the entry for all the correspondences.

    :param aggregations: aggregations dict returned by solr
    :param field: the field on which to perform the agregations
    :param correspondences: correspondence between article types
    :returns: aggregations dict with where the values of the
    """
    def reduce_correspondences(value, element):
        if element in aggregations[field].keys():
            count = aggregations[field][element]
            return value + count
        return value

    for v in aggregations[field].keys():
        if v in correspondences:
            aggregations[field][v] = functools.reduce(
                reduce_correspondences,
                correspondences[v],
                aggregations[field][v]
            )

    for replacements in correspondences.values():
        for replacement in replacements:
            if replacement in aggregations[field]:
                del(aggregations[field][replacement])


def add_correspondences_to_search_query(request, field, correspondences):
    """ If a field has correspondences, add them to the search query """
    rget = request.GET.copy()
    field_values = []
    for value in rget.getlist(field):
        field_values.append(value)
        for correspondence in correspondences.get(value, list()):
            if correspondence:
                field_values.append(correspondence)
    rget.setlist(field, field_values)
    return rget
