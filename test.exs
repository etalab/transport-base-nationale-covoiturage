Mix.install([
	{:csv, "~> 3.2"},
	{:httpoison, "~> 2.0"},
	{:jason, "~> 1.4"}
])

require Logger

File.stream!("bnlc-.csv")
|> CSV.decode!(unredact_exceptions: true)
|> Enum.to_list()
|> to_string()

Logger.info("Can decode the file")

github_url = "https://raw.githubusercontent.com/etalab/transport-base-nationale-covoiturage/refs/heads/main/bnlc-.csv"
schema_url = "https://schema.data.gouv.fr/schemas/etalab/schema-lieux-covoiturage/latest/schema.json"

%{"report" => %{"valid" => true}} = return =
	HTTPoison.get!("https://api.validata.etalab.studio/validate?url=#{github_url}&schema=#{schema_url}")
	|> Map.fetch!(:body)
	|> Jason.decode!()
Logger.debug(return)
Logger.info("File is valid")