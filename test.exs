Mix.install([{:csv, "~> 3.2"}])

require Logger

File.stream!("bnlc-.csv")
|> CSV.decode!(unredact_exceptions: true)
|> Enum.to_list()
|> to_string()

Logger.info("File is okay")