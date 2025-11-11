// Reading Comprehension Lessons - Index
// Exports all lessons for use in the application

import { lesson001 } from './lesson_001.js';
import { lesson002 } from './lesson_002.js';
import { lesson003 } from './lesson_003.js';
import { lesson004 } from './lesson_004.js';
import { lesson005 } from './lesson_005.js';
import { lesson006 } from './lesson_006.js';
import { lesson007 } from './lesson_007.js';
import { lesson008 } from './lesson_008.js';
import { lesson009 } from './lesson_009.js';
import { lesson010 } from './lesson_010.js';

// Array of all lessons
export const allLessons = [
  lesson001,
  lesson002,
  lesson003,
  lesson004,
  lesson005,
  lesson006,
  lesson007,
  lesson008,
  lesson009,
  lesson010
];

// Helper function to get lesson by ID
export function getLessonById(lessonId) {
  return allLessons.find(lesson => lesson.id === lessonId);
}

// Helper function to get lesson by index (1-10)
export function getLessonByIndex(index) {
  if (index < 1 || index > 10) {
    return null;
  }
  return allLessons[index - 1];
}

// Export individual lessons for direct access
export {
  lesson001,
  lesson002,
  lesson003,
  lesson004,
  lesson005,
  lesson006,
  lesson007,
  lesson008,
  lesson009,
  lesson010
};

