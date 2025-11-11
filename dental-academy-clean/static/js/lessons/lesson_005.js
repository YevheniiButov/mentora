// Reading Comprehension Lesson 005: Climate Change and Ocean Currents
export const lesson005 = {
  id: 'lesson_005',
  title: 'Climate Change and Ocean Currents',
  language: 'English',
  professionContext: 'Medical professionals reading scientific content',
  estimatedTime: 15,
  imageUrl: '/static/images/passages/ocean-currents.png',
  
  text: `A Ocean currents function as the planet's circulatory system, redistributing heat and regulating climate patterns across the globe. These massive movements of water, driven by wind, temperature differences, and the Earth's rotation, transport warm water from equatorial regions toward the poles while carrying cold water back toward the equator. The Atlantic Meridional Overturning Circulation (AMOC), commonly known as the Gulf Stream system, exemplifies this process by carrying warm water northward along the Atlantic coast, moderating temperatures in Western Europe and making cities like London significantly warmer than locations at similar latitudes. Without this thermal regulation, much of Northern Europe would experience climates comparable to those of northern Canada or Siberia.

B Climate scientists have observed concerning changes in ocean current patterns over recent decades, with potential implications for global weather systems. Rising atmospheric temperatures caused by greenhouse gas emissions are melting Arctic ice at accelerating rates, releasing massive quantities of fresh water into the North Atlantic. This influx of cold, fresh water disrupts the density-driven mechanisms that power the AMOC, as the system relies on cold, salty water sinking in the North Atlantic to maintain its circulation. Research published in 2021 indicated that the AMOC has weakened by approximately 15% since the mid-20th century, reaching its weakest state in over 1,600 years according to paleoclimate data. Computer models project that continued warming could lead to further weakening or even partial collapse of this critical current system within this century.

C The consequences of significant ocean current disruption would extend far beyond regional temperature changes. A weakened AMOC could paradoxically cause cooling in parts of Europe despite global warming trends, while simultaneously intensifying heat in other regions. Changes in ocean circulation patterns would alter precipitation distributions, potentially causing severe droughts in some areas and flooding in others. Marine ecosystems depend on nutrient cycling driven by ocean currents, and disruption could devastate fisheries that millions of people rely upon for food and livelihood. Furthermore, current weakening might accelerate sea-level rise along the North American Atlantic coast as water accumulates in regions where currents previously carried it away. These interconnected effects demonstrate how changes in one Earth system component can cascade through multiple environmental and social domains, underscoring the complexity of climate change impacts and the urgency of mitigation efforts.`,

  paragraphs: [
    {
      id: 'para_a',
      label: 'A',
      content: 'Ocean currents function as the planet\'s circulatory system, redistributing heat and regulating climate patterns across the globe. These massive movements of water, driven by wind, temperature differences, and the Earth\'s rotation, transport warm water from equatorial regions toward the poles while carrying cold water back toward the equator. The Atlantic Meridional Overturning Circulation (AMOC), commonly known as the Gulf Stream system, exemplifies this process by carrying warm water northward along the Atlantic coast, moderating temperatures in Western Europe and making cities like London significantly warmer than locations at similar latitudes. Without this thermal regulation, much of Northern Europe would experience climates comparable to those of northern Canada or Siberia.',
      mainTopic: 'Ocean currents as the planet\'s heat distribution system and their role in moderating climate',
      keyDates: []
    },
    {
      id: 'para_b',
      label: 'B',
      content: 'Climate scientists have observed concerning changes in ocean current patterns over recent decades, with potential implications for global weather systems. Rising atmospheric temperatures caused by greenhouse gas emissions are melting Arctic ice at accelerating rates, releasing massive quantities of fresh water into the North Atlantic. This influx of cold, fresh water disrupts the density-driven mechanisms that power the AMOC, as the system relies on cold, salty water sinking in the North Atlantic to maintain its circulation. Research published in 2021 indicated that the AMOC has weakened by approximately 15% since the mid-20th century, reaching its weakest state in over 1,600 years according to paleoclimate data. Computer models project that continued warming could lead to further weakening or even partial collapse of this critical current system within this century.',
      mainTopic: 'Climate change is weakening ocean currents through melting ice and disrupting circulation mechanisms',
      keyDates: ['2021', 'mid-20th century']
    },
    {
      id: 'para_c',
      label: 'C',
      content: 'The consequences of significant ocean current disruption would extend far beyond regional temperature changes. A weakened AMOC could paradoxically cause cooling in parts of Europe despite global warming trends, while simultaneously intensifying heat in other regions. Changes in ocean circulation patterns would alter precipitation distributions, potentially causing severe droughts in some areas and flooding in others. Marine ecosystems depend on nutrient cycling driven by ocean currents, and disruption could devastate fisheries that millions of people rely upon for food and livelihood. Furthermore, current weakening might accelerate sea-level rise along the North American Atlantic coast as water accumulates in regions where currents previously carried it away. These interconnected effects demonstrate how changes in one Earth system component can cascade through multiple environmental and social domains, underscoring the complexity of climate change impacts and the urgency of mitigation efforts.',
      mainTopic: 'Widespread consequences of ocean current disruption affecting weather, ecosystems, and human societies',
      keyDates: []
    }
  ],

  vocabulary: [
    {
      id: 'vocab_1',
      word: 'circulatory',
      partOfSpeech: 'adjective',
      definition: 'relating to the movement of fluids in a system',
      contextSentence: 'function as the planet\'s circulatory system',
      explanationInContext: 'Ocean currents move heat around the planet like blood circulates in the body',
      synonyms: ['circulating', 'flowing'],
      usage: 'Medical term for blood circulation; used metaphorically here for ocean currents',
      medicalConnection: 'Direct medical term - the circulatory system moves blood; here used as metaphor for ocean heat distribution'
    },
    {
      id: 'vocab_2',
      word: 'redistributing',
      partOfSpeech: 'verb',
      definition: 'distributing again or differently',
      contextSentence: 'redistributing heat and regulating climate patterns',
      explanationInContext: 'Ocean currents move heat from one place to another, spreading it around the planet',
      synonyms: ['reallocating', 'redistributing', 'spreading'],
      usage: 'Used when resources or energy are moved from one area to another',
      medicalConnection: null
    },
    {
      id: 'vocab_3',
      word: 'exemplifies',
      partOfSpeech: 'verb',
      definition: 'to be a typical example of something',
      contextSentence: 'exemplifies this process',
      explanationInContext: 'The AMOC is a perfect example of how ocean currents redistribute heat',
      synonyms: ['demonstrates', 'illustrates', 'represents'],
      usage: 'Used when something is a clear example of a concept',
      medicalConnection: null
    },
    {
      id: 'vocab_4',
      word: 'moderating',
      partOfSpeech: 'verb',
      definition: 'making less extreme or intense',
      contextSentence: 'moderating temperatures in Western Europe',
      explanationInContext: 'The Gulf Stream makes temperatures less extreme - warmer in winter, cooler in summer',
      synonyms: ['regulating', 'balancing', 'tempering'],
      usage: 'Used when something reduces extremes or makes conditions more balanced',
      medicalConnection: null
    },
    {
      id: 'vocab_5',
      word: 'influx',
      partOfSpeech: 'noun',
      definition: 'a large arrival or entry of something',
      contextSentence: 'This influx of cold, fresh water disrupts',
      explanationInContext: 'A large amount of fresh water is entering the North Atlantic from melting ice',
      synonyms: ['inflow', 'arrival', 'entry', 'stream'],
      usage: 'Used when a large amount of something enters a system',
      medicalConnection: null
    },
    {
      id: 'vocab_6',
      word: 'density-driven',
      partOfSpeech: 'adjective',
      definition: 'powered by differences in density (mass per volume)',
      contextSentence: 'disrupts the density-driven mechanisms',
      explanationInContext: 'Ocean currents work because cold, salty water is denser and sinks, creating circulation',
      synonyms: ['density-based', 'density-powered'],
      usage: 'Scientific term for systems powered by density differences',
      medicalConnection: null
    },
    {
      id: 'vocab_7',
      word: 'paleoclimate',
      partOfSpeech: 'noun',
      definition: 'ancient climate conditions',
      contextSentence: 'according to paleoclimate data',
      explanationInContext: 'Data from studying ancient climates (thousands of years ago)',
      synonyms: ['ancient climate', 'historical climate'],
      usage: 'Scientific term for studying past climate conditions',
      medicalConnection: null
    },
    {
      id: 'vocab_8',
      word: 'paradoxically',
      partOfSpeech: 'adverb',
      definition: 'in a way that seems contradictory but may be true',
      contextSentence: 'could paradoxically cause cooling in parts of Europe despite global warming',
      explanationInContext: 'It seems contradictory that global warming could cause cooling, but it\'s possible',
      synonyms: ['contradictorily', 'seemingly contradictory'],
      usage: 'Used when something seems to contradict itself but is actually true',
      medicalConnection: null
    },
    {
      id: 'vocab_9',
      word: 'cascade',
      partOfSpeech: 'verb',
      definition: 'to flow or fall in stages',
      contextSentence: 'can cascade through multiple environmental and social domains',
      explanationInContext: 'One change causes another, which causes another, like a waterfall of effects',
      synonyms: ['flow', 'spread', 'ripple', 'chain reaction'],
      usage: 'Used when one effect causes multiple other effects in sequence',
      medicalConnection: null
    },
    {
      id: 'vocab_10',
      word: 'mitigation',
      partOfSpeech: 'noun',
      definition: 'the action of reducing the severity of something',
      contextSentence: 'the urgency of mitigation efforts',
      explanationInContext: 'Efforts to reduce or prevent the worst effects of climate change',
      synonyms: ['reduction', 'alleviation', 'lessening'],
      usage: 'Used when discussing efforts to reduce negative impacts',
      medicalConnection: 'Medical term - mitigation of symptoms or disease progression'
    }
  ],

  questions: [
    {
      id: 'q1',
      level: 1,
      type: 'vocabulary_context',
      difficulty: 'easy',
      paragraph: 'para_a',
      question: 'What does "circulatory" mean when describing ocean currents?',
      text: 'function as the planet\'s circulatory system',
      options: [
        {
          id: 'q1_a',
          text: 'Relating to the movement of fluids in a system like blood circulation',
          correct: true,
          explanation: 'Correct. "Circulatory" refers to the movement and flow of fluids. The author uses this medical term as a metaphor - ocean currents move heat around the planet like blood circulates in the body, redistributing warmth and cold to regulate global climate patterns. This metaphor helps readers understand how ocean currents function as a distribution system.'
        },
        {
          id: 'q1_b',
          text: 'Relating to circular shapes and round forms',
          correct: false,
          explanation: '"Circulatory" refers to movement, flow, and distribution of fluids, not shape or geometric forms. The metaphor is about circulation (the process of moving and distributing), not circles or round shapes. The word describes a process, not a shape.'
        },
        {
          id: 'q1_c',
          text: 'Relating only to the heart and cardiac function',
          correct: false,
          explanation: 'While the circulatory system includes the heart, "circulatory" refers to the entire system of fluid movement and distribution throughout the body, not just the heart. The term describes the complete process of circulation, not a single organ. In the metaphor, ocean currents represent the entire circulation system, not just one part.'
        },
        {
          id: 'q1_d',
          text: 'Relating to breathing and respiratory processes',
          correct: false,
          explanation: 'That would be "respiratory." "Circulatory" specifically refers to the movement and distribution of fluids (blood in the body, or in this metaphor, ocean currents moving heat). Breathing involves the respiratory system, which is separate from the circulatory system that moves fluids.'
        }
      ],
      hint: 'Think about what system in your body moves fluids around. What is that system called?',
      relatedVocabulary: ['vocab_1'],
      learningPoint: 'Understanding medical metaphors helps in scientific texts - authors compare complex systems to familiar body systems'
    },
    {
      id: 'q2',
      level: 1,
      type: 'vocabulary_context',
      difficulty: 'easy',
      paragraph: 'para_b',
      question: 'What does "influx" mean in the context of melting ice?',
      text: 'This influx of cold, fresh water disrupts',
      options: [
        {
          id: 'q2_a',
          text: 'A large arrival or entry of something into a system',
          correct: true,
          explanation: 'Correct. "Influx" means a large amount of something entering or arriving in a system. Here, large amounts of fresh water are entering the North Atlantic from melting Arctic ice, disrupting the ocean current mechanisms. The text mentions "massive quantities," emphasizing the significant scale of this influx.'
        },
        {
          id: 'q2_b',
          text: 'A small trickle or minimal amount of water',
          correct: false,
          explanation: '"Influx" implies a large amount, significant volume, or substantial entry, not a small trickle or minimal amount. The text mentions "massive quantities" of fresh water being released, emphasizing the large scale of the influx and its disruptive impact on ocean circulation.'
        },
        {
          id: 'q2_c',
          text: 'The removal or extraction of water from the ocean',
          correct: false,
          explanation: '"Influx" means entry, arrival, or inflow of something into a system, not removal or extraction. The water from melting ice is entering and flowing into the North Atlantic, not leaving it. The word describes addition, not subtraction.'
        },
        {
          id: 'q2_d',
          text: 'A measurement of temperature or heat levels',
          correct: false,
          explanation: '"Influx" refers to the amount, volume, or flow of something entering a system, not temperature or heat measurements. Temperature is mentioned separately in the text as a factor, but "influx" specifically describes the large-scale entry of fresh water from melting ice.'
        }
      ],
      hint: 'The text says "massive quantities" are being released. What word describes a large arrival of something?',
      relatedVocabulary: ['vocab_5'],
      learningPoint: '"Influx" emphasizes scale - understanding this helps recognize when authors highlight significant changes'
    },
    {
      id: 'q3',
      level: 2,
      type: 'main_idea',
      difficulty: 'medium',
      paragraph: 'para_a',
      question: 'What is the main idea of paragraph A?',
      options: [
        {
          id: 'q3_a',
          text: 'London is warmer than other cities',
          correct: false,
          explanation: 'This is a specific example mentioned, not the main idea. The paragraph is about ocean currents\' role in climate regulation globally.'
        },
        {
          id: 'q3_b',
          text: 'Ocean currents function as the planet\'s heat distribution system regulating global climate',
          correct: true,
          explanation: 'This captures the paragraph\'s main points: (1) Ocean currents function as the planet\'s circulatory system, (2) They redistribute heat globally, moving warmth from equator to poles and cold from poles to equator, (3) They regulate global climate patterns, (4) The AMOC/Gulf Stream example shows how they moderate temperatures in Western Europe. This covers the entire paragraph\'s purpose of explaining ocean currents\' critical role in climate regulation.'
        },
        {
          id: 'q3_c',
          text: 'Ocean currents only affect Europe and nearby regions',
          correct: false,
          explanation: 'The paragraph discusses global climate regulation and heat distribution worldwide. Europe is mentioned as one example (showing how the AMOC moderates Western European temperatures), but the main idea is about ocean currents\' global function in redistributing heat and regulating climate patterns across the entire planet.'
        },
        {
          id: 'q3_d',
          text: 'Ocean currents are caused only by wind patterns and air movement',
          correct: false,
          explanation: 'The text mentions multiple driving forces: wind patterns, temperature differences between regions, AND Earth\'s rotation (Coriolis effect). Wind is just one factor among several that drive ocean circulation. The paragraph explains that currents are driven by a combination of factors, not just wind.'
        }
      ],
      hint: 'The paragraph starts with "function as the planet\'s circulatory system." What is the main function described?',
      relatedVocabulary: ['vocab_1', 'vocab_2', 'vocab_3', 'vocab_4'],
      learningPoint: 'Main ideas often start with a metaphor or key concept - here: circulatory system metaphor introduces the main function'
    },
    {
      id: 'q4',
      level: 2,
      type: 'main_idea',
      difficulty: 'medium',
      paragraph: 'para_b',
      question: 'What is the central theme of paragraph B?',
      options: [
        {
          id: 'q4_a',
          text: 'The AMOC has always been weak',
          correct: false,
          explanation: 'The text says it has "weakened" and is at its "weakest state in over 1,600 years," showing it was stronger before and is now declining.'
        },
        {
          id: 'q4_b',
          text: 'Climate change is weakening ocean currents through melting ice disrupting circulation mechanisms',
          correct: true,
          explanation: 'This captures the paragraph\'s themes: (1) Climate change causing changes through global warming, (2) Melting Arctic ice releasing massive quantities of fresh water, (3) This influx disrupting the density-driven mechanisms that power ocean circulation, (4) AMOC already weakened 15% and at its weakest state in over 1,600 years, (5) Future risk of further weakening or potential collapse. The paragraph connects cause (melting ice) to mechanism (disruption) to effect (weakening) to future risk.'
        },
        {
          id: 'q4_c',
          text: 'Ocean currents are getting stronger and more powerful over time',
          correct: false,
          explanation: 'The text explicitly states currents are "weakening," not strengthening or becoming more powerful. The paragraph describes a 15% weakening of the AMOC and identifies it as being at its weakest state in over 1,600 years, showing a clear trend of decline, not strengthening.'
        },
        {
          id: 'q4_d',
          text: 'Only the Arctic region is affected by these changes',
          correct: false,
          explanation: 'While Arctic ice melting is the cause of the disruption, the effects are global - the AMOC affects the entire Atlantic Ocean and global climate patterns. The weakening of ocean currents has cascading consequences for weather, ecosystems, and human societies worldwide, not just in the Arctic.'
        }
      ],
      hint: 'The paragraph discusses a problem (weakening) and its cause (melting ice). What is the overall message?',
      relatedVocabulary: ['vocab_5', 'vocab_6', 'vocab_7'],
      learningPoint: 'Main themes often connect cause (melting ice) → mechanism (disruption) → effect (weakening) → future risk'
    },
    {
      id: 'q5',
      level: 3,
      type: 'inference',
      difficulty: 'hard',
      paragraph: 'para_b',
      question: 'Why does the author mention that the AMOC is at its "weakest state in over 1,600 years"?',
      options: [
        {
          id: 'q5_a',
          text: 'To emphasize the severity and historical significance of unprecedented decline',
          correct: true,
          explanation: 'Correct. By mentioning 1,600 years, the author emphasizes that this weakening is historically significant and unprecedented - worse than anything recorded in over a millennium. This highlights both the severity of the current situation and the urgency of the problem, showing that the Atlantic Meridional Overturning Circulation (AMOC) is at a critically weak state that hasn\'t been seen in over 1,600 years of historical records.'
        },
        {
          id: 'q5_b',
          text: 'To show that ocean currents change in regular 1,600-year cycles',
          correct: false,
          explanation: 'The text doesn\'t suggest a regular cycle or pattern. It shows this is an exceptional, unprecedented weakening that is not part of a normal pattern. The 1,600-year timeframe refers to the historical record, not a cyclical pattern of change.'
        },
        {
          id: 'q5_c',
          text: 'To criticize the reliability of historical climate data records',
          correct: false,
          explanation: 'The author uses historical data to emphasize the severity of the problem and show how unprecedented the current weakening is, not to criticize the data itself or research methods. The tone is concerned about the climate situation, not critical of scientific data collection.'
        },
        {
          id: 'q5_d',
          text: 'To explain how ocean currents form and develop',
          correct: false,
          explanation: 'The text doesn\'t explain formation processes or how ocean currents develop. It emphasizes the current alarming state (weakest in 1,600 years) to show severity and historical significance, not to explain the origins or formation mechanisms of ocean currents.'
        }
      ],
      hint: 'What does it mean when something is at its "weakest state" in over 1,600 years? What does this tell you about how serious the situation is?',
      relatedVocabulary: ['vocab_7'],
      learningPoint: 'Authors use historical comparisons to emphasize severity - "weakest in X years" shows unprecedented decline'
    },
    {
      id: 'q6',
      level: 3,
      type: 'inference',
      difficulty: 'hard',
      paragraph: 'para_c',
      question: 'What does the author imply by saying effects "cascade through multiple environmental and social domains"?',
      options: [
        {
          id: 'q6_a',
          text: 'One change triggers a chain reaction affecting environmental, economic, and social systems',
          correct: true,
          explanation: 'Correct. "Cascade" means one effect causes another, which causes another in a chain reaction. The author shows that ocean current disruption doesn\'t just affect one isolated thing - it triggers a cascading chain reaction affecting weather patterns, ecosystems, food supplies, fisheries, sea levels, and human societies. This emphasizes the interconnectedness of Earth systems, where changes in one domain (environmental) flow into and affect other domains (economic, social), creating a complex web of consequences.'
        },
        {
          id: 'q6_b',
          text: 'Only environmental systems and natural processes are affected',
          correct: false,
          explanation: 'The text explicitly mentions "environmental and social domains," showing both natural and human systems are affected. "Cascade" means effects spread and flow through multiple interconnected areas, not just environmental ones. The disruption affects weather, ecosystems, food supplies, fisheries, and human societies - a broad range of interconnected systems.'
        },
        {
          id: 'q6_c',
          text: 'Effects are isolated and don\'t spread beyond the ocean',
          correct: false,
          explanation: '"Cascade" means effects flow and spread like a waterfall, creating a chain reaction - the opposite of isolated. The word emphasizes interconnectedness and the way one change triggers multiple subsequent effects. The text describes effects spreading to weather, ecosystems, food supplies, and societies, showing widespread impact.'
        },
        {
          id: 'q6_d',
          text: 'Only ocean temperatures and water conditions change',
          correct: false,
          explanation: 'The paragraph describes multiple cascading effects beyond ocean temperatures: precipitation patterns, ecosystems, fisheries, sea levels, weather systems, and social impacts. "Cascade" shows these all connect and flow from the initial disruption, creating a complex web of consequences across environmental, economic, and social domains.'
        }
      ],
      hint: 'Think about what "cascade" means - like a waterfall where one thing flows into another. What does this tell you about how effects spread?',
      relatedVocabulary: ['vocab_9'],
      learningPoint: '"Cascade" emphasizes interconnectedness - understanding this helps recognize when authors show complex system interactions'
    },
    {
      id: 'q7',
      level: 4,
      type: 'synthesis',
      difficulty: 'very_hard',
      paragraph: null,
      question: 'How does the author develop the argument about ocean current disruption across all three paragraphs?',
      options: [
        {
          id: 'q7_a',
          text: 'From function to problem to consequences showing disruption with far-reaching impacts',
          correct: true,
          explanation: 'Perfect synthesis. Paragraph A establishes ocean currents\' critical function (heat distribution, climate regulation, acting as the planet\'s circulatory system). Paragraph B shows the problem (weakening from climate change, melting ice disrupting mechanisms, unprecedented decline in over 1,600 years). Paragraph C describes consequences (cascading effects on weather, ecosystems, food supplies, fisheries, sea levels, and human societies). This builds a complete argument: function → disruption → consequences, showing how a critical climate regulator is being disrupted with far-reaching impacts across environmental, economic, and social systems.'
        },
        {
          id: 'q7_b',
          text: 'From past historical conditions to present situation to future predictions',
          correct: false,
          explanation: 'While there\'s a timeline element showing historical context (1,600 years) and current state, the main progression is thematic and structural: function (what currents do) → problem (what\'s going wrong) → consequences (what happens as a result), not just chronological. The structure emphasizes understanding the system and its disruption, not time periods.'
        },
        {
          id: 'q7_c',
          text: 'From small problems to big problems to even bigger problems',
          correct: false,
          explanation: 'The progression isn\'t about problem size or scale - it\'s about understanding the system (function and importance), then recognizing the disruption (weakening), then understanding the wide-ranging cascading consequences. The structure is about building comprehension: what it does → what\'s wrong → what happens, not about problem escalation.'
        },
        {
          id: 'q7_d',
          text: 'From solutions to problems to additional solutions',
          correct: false,
          explanation: 'The text doesn\'t present detailed solutions - it ends with mentioning "urgency of mitigation efforts" but doesn\'t elaborate on specific solutions. The progression is function → disruption → consequences, building an argument about the seriousness of the problem, not a cycle of problems and solutions.'
        }
      ],
      hint: 'Look at what each paragraph establishes: A = what currents do, B = what\'s going wrong, C = what happens as a result. How does this build a complete picture?',
      relatedVocabulary: ['vocab_1', 'vocab_2', 'vocab_5', 'vocab_6', 'vocab_9', 'vocab_10'],
      learningPoint: 'Effective arguments often follow: system function → disruption → consequences - recognizing this structure helps understand the complete message'
    },
    {
      id: 'q8',
      level: 4,
      type: 'synthesis',
      difficulty: 'very_hard',
      paragraph: null,
      question: 'What is the author\'s overall argument about ocean current disruption?',
      options: [
        {
          id: 'q8_a',
          text: 'Ocean currents are critical climate regulators being weakened with cascading consequences requiring urgent action',
          correct: true,
          explanation: 'This captures the complete argument: (1) Ocean currents are critical climate regulators (heat distribution, acting as the planet\'s circulatory system), (2) They\'re being weakened by climate change (melting ice, unprecedented decline in over 1,600 years), (3) Consequences are widespread and cascading (weather patterns, ecosystems, food supplies, fisheries, sea levels, human societies), (4) Effects cascade through interconnected environmental, economic, and social systems, (5) Urgency of addressing climate change is underscored. The author combines scientific explanation with a call for understanding the seriousness and interconnectedness of the problem.'
        },
        {
          id: 'q8_b',
          text: 'Ocean currents are not important for climate and weather systems',
          correct: false,
          explanation: 'The text emphasizes currents are "critical" and function as the "planet\'s circulatory system" that regulates climate and distributes heat - clearly important and essential, not unimportant. The entire argument is built on recognizing their critical role in global climate regulation.'
        },
        {
          id: 'q8_c',
          text: 'Only Europe and nearby regions will be affected by disruption',
          correct: false,
          explanation: 'The text describes global effects: weather patterns worldwide, ecosystems globally, fisheries, sea levels, and impacts on human societies across different regions. Europe is mentioned as one example of potential effects, but the text emphasizes cascading consequences that affect multiple environmental and social domains globally, not just one region.'
        },
        {
          id: 'q8_d',
          text: 'Ocean currents cannot be disrupted or weakened by climate change',
          correct: false,
          explanation: 'The entire text describes how currents ARE being disrupted and weakened, with explicit evidence showing the Atlantic Meridional Overturning Circulation (AMOC) is at its weakest state in over 1,600 years. Paragraph B explicitly shows weakening, risk of collapse, and the mechanisms by which climate change (melting ice) is disrupting the system. The text is built around documenting this disruption and its consequences.'
        }
      ],
      hint: 'Combine the function (A), the disruption (B), and the consequences (C). What is the author trying to communicate about the seriousness of this issue?',
      relatedVocabulary: ['vocab_1', 'vocab_2', 'vocab_5', 'vocab_6', 'vocab_8', 'vocab_9', 'vocab_10'],
      learningPoint: 'Overall arguments synthesize scientific facts with implications - here: critical system → disruption → widespread consequences → urgency'
    }
  ],

  recommendedSequence: ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8'],

  spacedRepetition: {
    easy: { initial: 1, intervals: [1, 3, 7] },
    medium: { initial: 0.5, intervals: [1, 3, 7, 14] },
    hard: { initial: 0, intervals: [1, 3, 7, 14, 30] },
    veryHard: { initial: 0, intervals: [1, 3, 7, 14, 30, 60] }
  },

  trackingMetrics: {
    vocabularyMastery: {},
    questionAttempts: {},
    comprehensionLevel: 'determining',
    timeSpent: 0,
    strengths: [],
    weaknesses: []
  }
};

