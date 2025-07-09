{{- define "plugin-marketplace.name" -}}
{{- default .Chart.Name .Values.nameOverride -}}
{{- end -}}

{{- define "plugin-marketplace.fullname" -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride -}}
{{- else -}}
{{ printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end -}}
{{- end -}}
