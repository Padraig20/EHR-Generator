import { Component } from '@angular/core';
import { Router } from "@angular/router";
import { AnalyzerService } from "../../services/analyzer.service";
import { ToastrService } from 'ngx-toastr';

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
export class HomeComponent {
  analyzing = false;
  analyzed = false;
  text = '';
  analyzedText = '';
  colors: Colors = {
    'MEDCOND': 'green',
    'MEDICATION': 'blue',
    'PROCEDURE': 'yellow',
    'SYMPTOM': 'red'
  }
  formattedJson = ''
  normalized_entities: NormalizedEntity[] = []
  groupedEntities: { [key: string]: [string, string | null, string | null, string][] } = {};

  constructor(
    private router: Router,
    private analyzerService: AnalyzerService,
    private notification: ToastrService,
  ) {
  }

  sanitizeHTML(htmlString: string): string {
    const allowedTagsRegex = /<(?!\/?(span|mark)\b)[^>]+>/gi;
    return htmlString.replace(allowedTagsRegex, '');
  }

  loadExample() {
    this.text = 'Patient is a 45-year-old man with a history of anaplastic astrocytoma of the spine complicated by sever' +
      'e lower extremity weakness and urinary retention s/p Foley catheter, high-dose steroids, hypertension, and chroni' +
      'c pain. The tumor is located in the T-L spine, unresectable anaplastic astrocytoma s/p radiation. Complicated by ' +
      'progressive lower extremity weakness and urinary retention. Patient initially presented with RLE weakness where h' +
      'is right knee gave out with difficulty walking and right anterior thigh numbness. MRI showed a spinal cord conus ' +
      'mass which was biopsied and found to be anaplastic astrocytoma.'
  }

  checkSpan(entity: Entity, text: string): boolean {
    const [entityText, entityType, startSpan, endSpan] = entity;
    return text.slice(startSpan, endSpan) == entityText;
  }

  correctSpan(entity: Entity, text: string): Entity {
    const [entityText, entityType, startSpan, endSpan] = entity;
    let start = startSpan;
    let end = endSpan + 1;

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

    return entity;
  }

  highlightEntities(text: string, entities: Entity[], colors: Colors): string {
    entities.sort((a, b) => b[2] - a[2]);

    for (let entity of entities) {
      
      if (!this.checkSpan(entity, text)) {
        entity = this.correctSpan(entity, text);
      }

      const [entityText, entityType, startSpan, endSpan] = entity;
      const color = colors[entityType] || 'grey'; //default color

      console.log(text.slice(startSpan, endSpan) == entityText, entityText, text.slice(startSpan, endSpan))

      let text1 = text.slice(0, startSpan)
      let text2 = text.slice(endSpan)

      if (entityText.startsWith(' ')) {
        text1 = text1 + ' '
      }

      //if (!entityText.endsWith(' ')) {
      //  text2 = ' ' + text2
      //}

      const highlightedText = `<mark class="highlight ${color}">${entityText.trim()}<span class="descriptor">${entityType}</span></mark>`;

      text = text1 + highlightedText + text2;
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

  goToWebsite(event: MouseEvent, code: string|null, entity: string): void {
    event.preventDefault();
    if (!code) {
      this.notification.error('No ICD/NDC code found!');
      return;
    }
    let link = ''
    if (entity === 'MEDICATION') {
      link = `https://ndclist.com/ndc/${code}`
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
          this.notification.error('Error analyzing note');
        }
      });
    }
  }
}
