let format ~stories ~current_date ~total_articles ~sources ~version =
  let b = Buffer.create 4096 in
  Buffer.add_string b (Printf.sprintf "<html><body><h1>Wieści Dnia: %s</h1>" current_date);
  List.iteri
    (fun i s ->
      Buffer.add_string b (Printf.sprintf "<h2>%d. %s</h2>" (i + 1) s.Summarize.overview);
      Buffer.add_string b "<ul>";
      List.iter (fun h -> Buffer.add_string b (Printf.sprintf "<li>%s</li>" h)) s.Summarize.highlights;
      Buffer.add_string b "</ul><p><strong>Źródła:</strong></p>";
      List.iter
        (fun u -> Buffer.add_string b (Printf.sprintf "<p><a href='%s'>%s</a></p>" u u))
        s.Summarize.urls)
    stories;
  Buffer.add_string b
    (Printf.sprintf
       "<p><strong>Przetworzono łącznie %d artykułów z %d źródeł.</strong></p>\n<p>Script "
       total_articles sources);
  Buffer.add_string b (Printf.sprintf "version: %s</p></body></html>" version);
  Buffer.contents b
