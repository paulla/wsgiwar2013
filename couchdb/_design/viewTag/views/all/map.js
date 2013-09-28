function(doc) {
    if (doc.doc_type == "Link")
    {
	doc.tags.forEach(function(tag)
			 {
			     emit(tag, doc);
			 })
    }
}
