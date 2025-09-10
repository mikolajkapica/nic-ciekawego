type story = {
  overview : string;
  highlights : string list;
  urls : string list;
  image_url : string option;
} [@@deriving yojson]

type output = { stories : story list } [@@deriving yojson]

let summarize_corpus ~api_key (_articles : Article.t list) : (output, string) Lwt_result.t =
  let _ = api_key in
  (* Placeholder summarization: returns empty *)
  Lwt.return (Ok { stories = [] })
