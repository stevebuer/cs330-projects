```mermaid
erDiagram
    raw_spots {
        INTEGER id PK
        TIMESTAMP timestamp
        TEXT raw_text
    }

    dx_spots {
        INTEGER id PK
        INTEGER raw_spot_id FK
        TIMESTAMP timestamp
        VARCHAR dx_call
        NUMERIC frequency
        VARCHAR spotter_call
        TEXT comment
        VARCHAR mode
        VARCHAR signal_report
        VARCHAR grid_square
        VARCHAR band
    }

    callsigns {
        INTEGER id PK
        VARCHAR callsign UK
        TIMESTAMP first_seen
        TIMESTAMP last_seen
        INTEGER total_spots
        INTEGER total_spotted
    }

    raw_spots ||--o{ dx_spots : "references"
    dx_spots }o--|| callsigns : "dx_call"
    dx_spots }o--|| callsigns : "spotter_call"
```</content>
<parameter name="filePath">/home/steve/GITHUB/cs330-projects/homework3/er_diagram.md