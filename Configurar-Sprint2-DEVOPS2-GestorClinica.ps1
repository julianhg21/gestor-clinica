<#
Configura Sprint 2 / DEVOPS 2 en Azure DevOps para gestor-clinica.
- Crea la iteración Sprint 2 (26-29 septiembre 2026) si no existe.
- Crea/actualiza Feature, User Stories, Tasks y Test Cases.
- Vincula la Feature al Epic #158.
- Asigna responsables del equipo.
- Evita duplicados por Tipo + Título.
- No guarda ni imprime el PAT.
- Genera Sprint2-AzureDevOps-WorkItems.csv.

Uso:
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\Configurar-Sprint2-DEVOPS2-GestorClinica.ps1

Opcional:
  $env:AZDO_PAT = "TU_PAT"
#>

[CmdletBinding()]
param(
    [string]$Organization = "jhernandezg81",
    [string]$Project = "gestor-clinica",
    [int]$EpicId = 158,
    [string]$SprintName = "Sprint 2",
    [datetime]$SprintStart = "2026-09-26",
    [datetime]$SprintFinish = "2026-09-29",
    [switch]$SkipTestCases
)

$ErrorActionPreference = "Stop"
$ApiVersion = "7.1"
$Julian = "jhernandezg81@miumg.edu.gt"
$Carlos = "ccalderone2@miumg.edu.gt"
$Federico = "fiturbidec@miumg.edu.gt"

function Get-Pat {
    if ($env:AZDO_PAT) { return $env:AZDO_PAT }
    $secure = Read-Host "Ingrese su PAT de Azure DevOps (no se mostrará)" -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try { return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
}

$Pat = Get-Pat
if ([string]::IsNullOrWhiteSpace($Pat)) { throw "No se recibió un PAT." }
$basic = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$Pat"))
$Headers = @{ Authorization = "Basic $basic"; Accept = "application/json" }
$EncodedProject = [uri]::EscapeDataString($Project)
$BaseUrl = "https://dev.azure.com/$Organization/$EncodedProject"

function Invoke-AzDo {
    param(
        [Parameter(Mandatory)][ValidateSet("GET","POST","PATCH")][string]$Method,
        [Parameter(Mandatory)][string]$Uri,
        [object]$Body,
        [string]$ContentType = "application/json"
    )
    $p = @{ Method=$Method; Uri=$Uri; Headers=$Headers; ErrorAction="Stop" }
    if ($null -ne $Body) {
        $p.Body = ($Body | ConvertTo-Json -Depth 20 -Compress)
        $p.ContentType = $ContentType
    }
    try { Invoke-RestMethod @p }
    catch {
        $detail = $_.ErrorDetails.Message
        if (-not $detail) { $detail = $_.Exception.Message }
        throw "Azure DevOps devolvió un error en $Method $Uri`n$detail"
    }
}

function Escape-WiqlLiteral([string]$Value) { $Value.Replace("'", "''") }

function Get-WorkItemByTitle {
    param([string]$Type,[string]$Title)
    $safeType = Escape-WiqlLiteral $Type
    $safeTitle = Escape-WiqlLiteral $Title
    $wiql = @{ query = "SELECT [System.Id] FROM WorkItems WHERE [System.TeamProject] = '$Project' AND [System.WorkItemType] = '$safeType' AND [System.Title] = '$safeTitle' ORDER BY [System.ChangedDate] DESC" }
    $res = Invoke-AzDo POST "$BaseUrl/_apis/wit/wiql?api-version=$ApiVersion" $wiql
    if ($res.workItems -and $res.workItems.Count -gt 0) { return [int]$res.workItems[0].id }
    return $null
}

function Get-WorkItem([int]$Id) {
    Invoke-AzDo GET "$BaseUrl/_apis/wit/workitems/$Id?`$expand=relations&api-version=$ApiVersion"
}

function Ensure-ParentLink {
    param([int]$ChildId,[int]$ParentId)
    $item = Get-WorkItem $ChildId
    $hasParent = $false
    foreach ($rel in @($item.relations)) {
        if ($rel.rel -eq "System.LinkTypes.Hierarchy-Reverse" -and $rel.url -match "/workItems/$ParentId$") { $hasParent = $true }
    }
    if (-not $hasParent) {
        $patch = @(@{ op="add"; path="/relations/-"; value=@{ rel="System.LinkTypes.Hierarchy-Reverse"; url="https://dev.azure.com/$Organization/_apis/wit/workItems/$ParentId"; attributes=@{ comment="Padre Sprint 2" } } })
        Invoke-AzDo PATCH "$BaseUrl/_apis/wit/workitems/$ChildId?api-version=$ApiVersion" $patch "application/json-patch+json" | Out-Null
    }
}

function Ensure-WorkItem {
    param(
        [string]$Type,[string]$Title,[string]$AssignedTo,[string]$IterationPath,
        [string]$Description,[string]$AcceptanceCriteria,[int]$ParentId=0,
        [double]$Hours=0,[string]$State=""
    )

    $id = Get-WorkItemByTitle $Type $Title
    $patch = @(
        @{ op="add"; path="/fields/System.IterationPath"; value=$IterationPath },
        @{ op="add"; path="/fields/System.AssignedTo"; value=$AssignedTo },
        @{ op="add"; path="/fields/System.Tags"; value="Sprint 2; DEVOPS 2; CI/CD" }
    )
    if ($Description) { $patch += @{ op="add"; path="/fields/System.Description"; value=$Description } }
    if ($AcceptanceCriteria -and $Type -eq "User Story") { $patch += @{ op="add"; path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria"; value=$AcceptanceCriteria } }
    if ($Type -eq "Task" -and $Hours -gt 0) {
        $patch += @{ op="add"; path="/fields/Microsoft.VSTS.Scheduling.OriginalEstimate"; value=$Hours }
        $patch += @{ op="add"; path="/fields/Microsoft.VSTS.Scheduling.RemainingWork"; value=$Hours }
    }
    if ($State) { $patch += @{ op="add"; path="/fields/System.State"; value=$State } }

    if ($id) {
        Write-Host "ACTUALIZA [$Type] #$id - $Title" -ForegroundColor Yellow
        $item = Invoke-AzDo PATCH "$BaseUrl/_apis/wit/workitems/$id?api-version=$ApiVersion" $patch "application/json-patch+json"
        if ($ParentId -gt 0) { Ensure-ParentLink $id $ParentId }
        return $item
    }

    Write-Host "CREA      [$Type] $Title" -ForegroundColor Green
    $createPatch = @(@{ op="add"; path="/fields/System.Title"; value=$Title }, @{ op="add"; path="/fields/System.AreaPath"; value=$Project }) + $patch
    if ($ParentId -gt 0) {
        $createPatch += @{ op="add"; path="/relations/-"; value=@{ rel="System.LinkTypes.Hierarchy-Reverse"; url="https://dev.azure.com/$Organization/_apis/wit/workItems/$ParentId"; attributes=@{ comment="Vinculado por configuración Sprint 2" } } }
    }
    $encodedType = [uri]::EscapeDataString($Type)
    Invoke-AzDo POST "$BaseUrl/_apis/wit/workitems/`$$encodedType?api-version=$ApiVersion" $createPatch "application/json-patch+json"
}

function Ensure-SprintIteration {
    $iterationPath = "$Project\$SprintName"
    $encodedSprint = [uri]::EscapeDataString($SprintName)
    try {
        $node = Invoke-AzDo GET "$BaseUrl/_apis/wit/classificationnodes/Iterations/$encodedSprint?api-version=$ApiVersion"
        Write-Host "Iteración existente: $iterationPath" -ForegroundColor Cyan
    }
    catch {
        Write-Host "Creando iteración: $iterationPath" -ForegroundColor Green
        $body = @{ name=$SprintName; attributes=@{ startDate=$SprintStart.ToUniversalTime().ToString("o"); finishDate=$SprintFinish.Date.AddHours(23).AddMinutes(59).ToUniversalTime().ToString("o") } }
        $node = Invoke-AzDo POST "$BaseUrl/_apis/wit/classificationnodes/Iterations?api-version=$ApiVersion" $body
    }

    try {
        $teams = Invoke-AzDo GET "https://dev.azure.com/$Organization/_apis/projects/$EncodedProject/teams?api-version=7.1-preview.3"
        if ($teams.value.Count -gt 0) {
            $team = $teams.value | Where-Object { $_.name -eq "$Project Team" } | Select-Object -First 1
            if (-not $team) { $team = $teams.value | Select-Object -First 1 }
            $teamName = [uri]::EscapeDataString($team.name)
            try {
                Invoke-AzDo POST "https://dev.azure.com/$Organization/$EncodedProject/$teamName/_apis/work/teamsettings/iterations?api-version=$ApiVersion" @{ id=$node.identifier } | Out-Null
                Write-Host "Sprint asociado al equipo: $($team.name)" -ForegroundColor Cyan
            } catch { Write-Warning "La iteración fue creada, pero no se pudo asociar automáticamente al equipo." }
        }
    } catch { Write-Warning "No se pudo consultar el equipo por defecto. Se continuará." }

    return $iterationPath
}

Write-Host "`n=== CONFIGURACIÓN SPRINT 2 / DEVOPS 2 ===" -ForegroundColor Cyan
$IterationPath = Ensure-SprintIteration
$epic = Get-WorkItem $EpicId
Write-Host "Epic padre: #$EpicId - $($epic.fields.'System.Title')" -ForegroundColor Cyan

$Results = New-Object System.Collections.Generic.List[object]
function Add-Result($item,$type,$parentId="") {
    $assigned = $item.fields.'System.AssignedTo'
    if ($assigned -is [string]) { $assignedName = $assigned } else { $assignedName = $assigned.displayName }
    $Results.Add([pscustomobject]@{ Id=$item.id; Tipo=$type; Titulo=$item.fields.'System.Title'; Estado=$item.fields.'System.State'; Asignado=$assignedName; Padre=$parentId; Iteracion=$item.fields.'System.IterationPath' })
}

$feature = Ensure-WorkItem "Feature" "Sprint 2 - CI/CD, Plan de Pruebas y Mejora de Aplicación" $Julian $IterationPath `
    "Implementar CI/CD, plan formal de pruebas, staging, evidencia Scrum, documentación DEVOPS 2 y mejoras funcionales/visuales." "" $EpicId 0 "Active"
$FeatureId = [int]$feature.id
Add-Result $feature "Feature" $EpicId

$stories = @(
    @{ Key="CICD"; Title="Implementar pipeline CI/CD con Jenkins y despliegue a staging"; Assigned=$Federico; AC="<ul><li>Jenkinsfile versionado.</li><li>Checkout, Build, Test y Deploy staging.</li><li>Docker build.</li><li>pytest con reporte HTML/JUnit.</li><li>Evidencia exitosa y fallida real.</li></ul>" },
    @{ Key="TEST"; Title="Formalizar y ejecutar el plan de pruebas del Sprint 2"; Assigned=$Carlos; AC="<ul><li>Objetivos, propósito, alcance y estrategia.</li><li>Unitarias, integración, sistema, aceptación, seguridad y rendimiento.</li><li>15+ casos.</li><li>pytest + Selenium.</li><li>Reporte HTML.</li></ul>" },
    @{ Key="CRUD"; Title="Mejorar CRUD, trazabilidad y experiencia visual de la aplicación"; Assigned=$Federico; AC="<ul><li>Edición y desactivación/anulación según reglas.</li><li>Inventario conserva trazabilidad.</li><li>Interfaz renovada y responsive.</li></ul>" },
    @{ Key="DOC"; Title="Preparar documentación DEVOPS 2 y video de evidencia"; Assigned=$Julian; AC="<ul><li>PDF DEVOPS 2 de 12-18 páginas.</li><li>Evidencia real.</li><li>Video #2 de 8-10 minutos.</li></ul>" },
    @{ Key="SCRUM"; Title="Gestionar y documentar Scrum del Sprint 2"; Assigned=$Carlos; AC="<ul><li>Sprint Backlog.</li><li>Burn down.</li><li>Daily Scrum.</li><li>Review y Retrospectiva.</li></ul>" }
)

$StoryIds = @{}
foreach ($s in $stories) {
    $story = Ensure-WorkItem "User Story" $s.Title $s.Assigned $IterationPath "Historia Sprint 2 / DEVOPS 2." $s.AC $FeatureId 0 "Active"
    $StoryIds[$s.Key] = [int]$story.id
    Add-Result $story "User Story" $FeatureId
}

$tasks = @(
    @{S="CICD";T="Versionar Jenkinsfile con etapas requeridas";A=$Federico;H=5},
    @{S="CICD";T="Integrar compilación y Docker build en CI/CD";A=$Federico;H=4},
    @{S="CICD";T="Generar reporte HTML y JUnit con pytest";A=$Federico;H=4},
    @{S="CICD";T="Configurar despliegue seguro a staging";A=$Federico;H=5},
    @{S="CICD";T="Capturar evidencia de pipeline exitoso y fallido";A=$Carlos;H=3},
    @{S="TEST";T="Redactar objetivos, alcance y estrategia del plan de pruebas";A=$Carlos;H=5},
    @{S="TEST";T="Implementar pruebas unitarias y de contrato";A=$Federico;H=5},
    @{S="TEST";T="Implementar pruebas de integración y rendimiento";A=$Federico;H=4},
    @{S="TEST";T="Implementar prueba de sistema con Selenium";A=$Federico;H=4},
    @{S="TEST";T="Ejecutar pruebas y documentar resultados reales";A=$Carlos;H=4},
    @{S="CRUD";T="Habilitar edición y desactivación de pacientes, productos y servicios";A=$Federico;H=6},
    @{S="CRUD";T="Habilitar edición y anulación de ventas, pagos y servicios realizados";A=$Federico;H=6},
    @{S="CRUD";T="Rediseñar login, navegación, tablas y componentes visuales";A=$Julian;H=6},
    @{S="CRUD";T="Ejecutar regresión funcional después de mejoras CRUD";A=$Federico;H=4},
    @{S="DOC";T="Recopilar capturas y evidencia técnica DEVOPS 2";A=$Julian;H=4},
    @{S="DOC";T="Elaborar documento PDF DEVOPS 2";A=$Julian;H=8},
    @{S="DOC";T="Preparar y grabar Video YouTube #2";A=$Julian;H=5},
    @{S="SCRUM";T="Organizar Sprint Backlog Sprint 2";A=$Carlos;H=3},
    @{S="SCRUM";T="Documentar Daily Scrum Sprint 2";A=$Carlos;H=3},
    @{S="SCRUM";T="Actualizar Burn Down Sprint 2";A=$Carlos;H=3},
    @{S="SCRUM";T="Documentar Sprint Review y Retrospectiva";A=$Carlos;H=3},
    @{S="SCRUM";T="Validar entregables finales como Product Owner";A=$Julian;H=2}
)

foreach ($t in $tasks) {
    $parent = $StoryIds[$t.S]
    $task = Ensure-WorkItem "Task" $t.T $t.A $IterationPath "Tarea planificada Sprint 2. Mantener Remaining Work actualizado." "" $parent $t.H "Active"
    Add-Result $task "Task" $parent
}

if (-not $SkipTestCases) {
    $testCases = @(
        "CP-01 - Login válido","CP-02 - Login inválido","CP-03 - Recurso protegido sin token","CP-04 - Crear paciente","CP-05 - Editar paciente","CP-06 - Desactivar paciente",
        "CP-07 - Crear producto","CP-08 - Editar producto","CP-09 - Desactivar producto","CP-10 - Registrar entrada de inventario","CP-11 - Evitar stock negativo","CP-12 - Crear servicio",
        "CP-13 - Editar servicio","CP-14 - Editar servicio realizado","CP-15 - Anular servicio realizado","CP-16 - Crear venta pendiente","CP-17 - Editar venta pendiente","CP-18 - Anular venta pendiente",
        "CP-19 - Registrar pago","CP-20 - Editar pago de venta pendiente","CP-21 - Impedir edición de pago cerrado","CP-22 - Desactivar usuario","CP-23 - Impedir auto-desactivación de administrador",
        "CP-24 - Cargar dashboard","CP-25 - Validar interfaz responsive y UX","CP-26 - Validar tiempo de respuesta del health"
    )
    foreach ($title in $testCases) {
        $tc = Ensure-WorkItem "Test Case" $title $Federico $IterationPath "Caso del plan docs/PLAN_PRUEBAS_SPRINT2.md. No cerrar hasta ejecutar y conservar evidencia real." "" $StoryIds["TEST"] 0 "Ready"
        Add-Result $tc "Test Case" $StoryIds["TEST"]
    }
}

$outFile = Join-Path (Get-Location) "Sprint2-AzureDevOps-WorkItems.csv"
$Results | Sort-Object Tipo,Id | Export-Csv $outFile -NoTypeInformation -Encoding UTF8

Write-Host "`n=== SPRINT 2 CONFIGURADO ===" -ForegroundColor Green
Write-Host "Iteración: $IterationPath"
Write-Host "Feature:   #$FeatureId"
Write-Host "Historias: $($StoryIds.Values -join ', ')"
Write-Host "Resumen:   $outFile"
Write-Host "`nIMPORTANTE:" -ForegroundColor Yellow
Write-Host "- Las Tasks quedan Active; no se fabrican cierres."
Write-Host "- Los Test Case quedan Ready; registrar PASS/FAIL solo después de ejecutarlos."
Write-Host "- Si Azure exige limpiar Remaining Work al cerrar, use Remove en lugar de 0."
Write-Host "- No comparta el PAT. Si algún PAT fue expuesto, rótelo/revóquelo."
