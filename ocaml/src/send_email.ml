let send ~smtp:_ ~username:_ ~password:_ ~to_addr:_ ~subject:_ ~html_body:_ =
  (* TODO: implement using mrmime (build MIME) + colombe (SMTP send) *)
  Lwt.return (Ok ())
