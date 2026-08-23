import ukDocs from '../data/uk/docs.json';
import ukRoles from '../data/uk/roles.json';
import ukCalendar from '../data/uk/calendar.json';
import ukKernel from '../data/uk/kernel.json';
import ukRegulation from '../data/uk/regulation.json';
import ukChecklists from '../data/uk/checklists.json';
import ukDict from '../data/uk/dict.json';
import ukProcesses from '../data/uk/processes.json';
import ukRoutes from '../data/uk/routes.json';
import ukUi from '../i18n/uk.json';

import ruDocs from '../data/ru/docs.json';
import ruRoles from '../data/ru/roles.json';
import ruCalendar from '../data/ru/calendar.json';
import ruKernel from '../data/ru/kernel.json';
import ruRegulation from '../data/ru/regulation.json';
import ruChecklists from '../data/ru/checklists.json';
import ruDict from '../data/ru/dict.json';
import ruProcesses from '../data/ru/processes.json';
import ruRoutes from '../data/ru/routes.json';
import ruUi from '../i18n/ru.json';

import enDocs from '../data/en/docs.json';
import enRoles from '../data/en/roles.json';
import enCalendar from '../data/en/calendar.json';
import enKernel from '../data/en/kernel.json';
import enRegulation from '../data/en/regulation.json';
import enChecklists from '../data/en/checklists.json';
import enDict from '../data/en/dict.json';
import enProcesses from '../data/en/processes.json';
import enRoutes from '../data/en/routes.json';
import enUi from '../i18n/en.json';

const DATA = {
  uk: { docs: ukDocs, roles: ukRoles, calendar: ukCalendar, kernel: ukKernel,
        regulation: ukRegulation, checklists: ukChecklists, dict: ukDict,
        processes: ukProcesses, routes: ukRoutes, ui: ukUi },
  ru: { docs: ruDocs, roles: ruRoles, calendar: ruCalendar, kernel: ruKernel,
        regulation: ruRegulation, checklists: ruChecklists, dict: ruDict,
        processes: ruProcesses, routes: ruRoutes, ui: ruUi },
  en: { docs: enDocs, roles: enRoles, calendar: enCalendar, kernel: enKernel,
        regulation: enRegulation, checklists: enChecklists, dict: enDict,
        processes: enProcesses, routes: enRoutes, ui: enUi },
};

export const LANGS = Object.keys(DATA);
export const DEFAULT_LANG = 'uk';
export function getData(lang) { return DATA[lang] ?? DATA[DEFAULT_LANG]; }
export function t(lang, key) {
  const ui = getData(lang).ui;
  return key.split('.').reduce((o, k) => (o ? o[k] : undefined), ui) ?? key;
}
