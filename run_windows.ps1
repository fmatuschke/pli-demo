

if (-not (Test-Path .\env)) {
	python.exe -m venv env
	.\env\Scripts\activate
	pip.exe install pip --upgrade
	pip.exe install -r requirements.txt
	deactivate
}


if ((Test-Path .\env)) {
	.\env\Scripts\activate
	python.exe main.py
}
else { "Error .\env does not exists" }