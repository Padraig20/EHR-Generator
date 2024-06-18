import { Component, OnInit } from '@angular/core';
import { Router } from "@angular/router";
import { AnalyzerService } from "../../services/analyzer.service";
import { ToastrService } from 'ngx-toastr';
import { HttpClient } from '@angular/common/http';

interface Colors {
  [key: string]: string;
}

type Entity = [string, string, number, number];
type NormalizedEntity = [string, string | null, string | null, string]

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  analyzing = false;
  analyzed = false;
  text = '';
  analyzedText = '';
  colors: Colors = {
    'MEDCOND': 'green',
    'MEDICATION': 'blue',
    'PROCEDURE': 'yellow',
    'SYMPTOM': 'orange'
  }
  formattedJson = ''
  normalized_entities: NormalizedEntity[] = []
  groupedEntities: { [key: string]: [string, string | null, string | null, string][] } = {};
  topics: string[] = []

  constructor(
    private router: Router,
    private analyzerService: AnalyzerService,
    private notification: ToastrService,
    private http: HttpClient
  ) {
  }

  ngOnInit(): void {
    this.http.get('assets/topics.txt', { responseType: 'text' })
      .subscribe(data => {
        this.topics = data.split('\n').map(topic => topic.trim()).filter(topic => topic.length > 0);
      });
  }

  sanitizeHTML(htmlString: string): string {
    const allowedTagsRegex = /<(?!\/?(span|mark)\b)[^>]+>/gi;
    return htmlString.replace(allowedTagsRegex, '');
  }

  loadExample() {
    const randomTopic = this.topics[Math.floor(Math.random() * this.topics.length)];
    this.text = randomTopic;
  }

  checkSpan(entity: Entity, text: string): boolean {
    const [entityText, entityType, startSpan, endSpan] = entity;
    return text.slice(startSpan, endSpan) == entityText;
  }

  correctSpan(entity: Entity, text: string): Entity {
    const [entityText, entityType, startSpan, endSpan] = entity;
    let start = startSpan;
    let end = endSpan;

    if (text.slice(start, end) == entityText) {
      return [entityText, entityType, start, end]
    }

    start = startSpan + 1;
    end = endSpan;
    if (text.slice(start, end) == entityText) {
      return [entityText, entityType, start, end]
    }

    start = startSpan - 1;
    end = endSpan - 1;
    if (text.slice(start, end) == entityText) {
      return [entityText, entityType, start, end]
    }

    start = startSpan + 1;
    end = endSpan + 1;
    if (text.slice(start, end) == entityText) {
      return [entityText, entityType, start, end]
    }

    start = startSpan;
    end = endSpan - 2;
    if (text.slice(start, end) == entityText) {
      return [entityText, entityType, start, end]
    }

    start = startSpan + 2;
    end = endSpan + 1;
    if (text.slice(start, end) == entityText) {
      return [entityText, entityType, start, end]
    }

    return entity;
  }

  highlightEntities(text: string, entities: Entity[], colors: Colors): string {
    entities = entities.filter((entity, index) => {
      for (let i = index + 1; i < entities.length; i++) {
        const [_, __, startSpan, endSpan] = entity;
        const [___, ____, otherStartSpan, otherEndSpan] = entities[i];
        if (
          (startSpan >= otherStartSpan && startSpan <= otherEndSpan) ||
          (endSpan >= otherStartSpan && endSpan <= otherEndSpan)
        ) {
          if (entity[1] !== entities[i][1]) {
            if (endSpan - startSpan > otherEndSpan - otherStartSpan) {
              entity[1] = entity[1] + '/' + entities[i][1];
            } else {
              entities[i][1] = entity[1] + '/' + entities[i][1];
              entity = entities[i];
            }
          }
          entities.splice(i, 1);
          i--;
        }
      }
      return true;
    });

    entities.sort((a, b) => b[3] - a[3]);


    let copied = text;

    for (let entity of entities) {

      if (!this.checkSpan(entity, copied)) {
        entity = this.correctSpan(entity, copied);
      }

      const [entityText, entityType, startSpan, endSpan] = entity;
      let color = colors[entityType] || 'grey'; //default color
      if (entityType.includes('/')) {
        color = 'grey';
      }

      console.log(text.slice(startSpan, endSpan) == entityText, entityText, text.slice(startSpan, endSpan), color)

      let text1 = copied.slice(0, startSpan)
      let text2 = text.slice(endSpan)

      if (entityText.startsWith(' ')) {
        text1 = text1 + ' '
      }

      //if (!entityText.endsWith(' ')) {
      //  text2 = ' ' + text2
      //}

      const highlightedText = `<mark class="highlight ${color}">${entityText.trim()}<span class="descriptor">${entityType}</span></mark>`;

      text = text1 + highlightedText + text2;

      console.log(text)
    }

    return text;
  }

  copyToClipboard() {
    navigator.clipboard.writeText(this.formattedJson).then(() => {
      this.notification.success('JSON copied to clipboard');
    }).catch(err => {
      console.error('Failed to copy!', err);
    });
  }

  groupEntitiesByType() {
    this.groupedEntities = this.normalized_entities.reduce((acc, entity) => {
      const type = entity[3];
      if (!acc[type]) {
        acc[type] = [];
      }
      acc[type].push(entity);
      return acc;
    }, {} as { [key: string]: [string, string | null, string | null, string][] });
  }

  getEntityTypes(): string[] {
    return Object.keys(this.groupedEntities);
  }

  goToWebsite(event: MouseEvent, code: string | null, entity: string): void {
    event.preventDefault();
    if (!code) {
      this.notification.error('No ICD/NDC code found!');
      return;
    }
    let link = ''
    if (entity === 'MEDICATION') {
      link = `https://ndclist.com/ndc/${code}`
    } else if (entity === 'PROCEDURE') {
      link = `https://icdlist.com/icd-10-pcs/${code}`
    } else {
      link = `https://icdlist.com/icd-10/${code}`
    }
    window.open(link, '_blank');
  }

  analyzeNote() {
    this.analyzing = true;

    if (this.text.toLowerCase() === 'github') {
      window.location.href = 'https://github.com/Padraig20';
    } else if (this.text.toLowerCase() === 'linkedin') {
      window.location.href = 'https://linkedin.com/in/patrick-styll';
    } else {

      this.analyzerService.analyzeNote(this.text).subscribe({
        next: data => {
          console.log(data);
          this.analyzedText = '';
          const ehr: JSON = data.ehr;
          const entities: Entity[] = data.entities;
          const normalizedEntities: NormalizedEntity[] = data.normalized_entities;

          this.formattedJson = JSON.stringify(ehr, null, 2);

          this.normalized_entities = normalizedEntities
          this.groupEntitiesByType()

          this.analyzedText = this.highlightEntities(this.text, entities, this.colors);

          this.notification.info('Successfully analyzed note!');
          console.log(this.analyzedText);
          this.analyzed = true;
          this.analyzing = false;
        },
        error: error => {
          console.log('Error analyzing note: ' + error);
          this.analyzing = false;
          this.notification.error('Have you started the local backend on port 5000?', 'Error analyzing note');
        }
      });
    }
  }
}
