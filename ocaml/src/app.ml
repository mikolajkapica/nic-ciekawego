let ( let* ) = Lwt.bind

let run () =
  let config_result = Config.load_file "config.yaml" in
  match config_result with
  | Error e -> Lwt_io.printf "Config error: %s\n" e
  | Ok cfg ->
      let* (articles, errors) = Rss_fetch.fetch_all cfg.Config.feeds in
      let* summary_res = Summarize.summarize_corpus ~api_key:"" articles in
      (match errors with
      | [] -> ()
      | _ -> List.iter (fun e -> Logs.warn (fun m -> m "RSS error: %s" e)) errors);
      (match summary_res with
      | Ok s ->
          let html =
            Format_email.format ~stories:s.Summarize.stories ~current_date:"TODAY" ~total_articles:(List.length articles)
              ~sources:(List.length cfg.Config.feeds) ~version:"0.1.0"
          in
          let* _send =
            Send_email.send ~smtp:"smtp.gmail.com" ~username:"" ~password:"" ~to_addr:cfg.email_to ~subject:"Daily News" ~html_body:html
          in
          Lwt.return_unit
      | Error e -> Lwt_io.printf "Summarization error: %s\n" e)
