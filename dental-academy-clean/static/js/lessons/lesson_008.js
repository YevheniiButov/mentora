// Reading Comprehension Lesson 008: Renewable Energy Technologies
export const lesson008 = {
  id: 'lesson_008',
  title: 'Renewable Energy Technologies',
  language: 'English',
  professionContext: 'Medical professionals reading scientific content',
  estimatedTime: 15,
  imageUrl: '/static/images/passages/renewable-energy.png',
  
  text: `A The transition from fossil fuels to renewable energy sources represents one of the most critical challenges and opportunities of the 21st century. Unlike coal, oil, and natural gas, which release carbon dioxide accumulated over millions of years, renewable energy technologies harness naturally replenishing resources such as sunlight, wind, water flow, and geothermal heat. Solar photovoltaic technology has experienced dramatic cost reductions over the past decade, with prices falling more than 80% since 2010, making it now the cheapest source of electricity in many regions. Wind power has similarly become economically competitive, with modern turbines capable of generating electricity at costs comparable to or lower than conventional power plants. These economic shifts, combined with growing concerns about climate change and air pollution, have accelerated renewable energy adoption worldwide.

B Despite impressive progress, renewable energy integration faces significant technical and practical obstacles. The fundamental challenge lies in intermittency—solar panels generate electricity only during daylight hours, and wind turbines depend on wind availability, creating mismatches between energy generation and consumption patterns. This variability requires either backup power sources or energy storage systems, both of which add costs and complexity. Battery technology, particularly lithium-ion batteries, has improved substantially, but storing electricity at grid scale remains expensive and materials-intensive. Furthermore, renewable installations require considerably more land than fossil fuel plants for equivalent energy output. A coal power station might occupy several acres, while a solar farm producing comparable electricity could require hundreds of acres. This spatial footprint raises concerns about habitat disruption and competing land uses, particularly as agriculture and urban development already constrain available space.

C Addressing renewable energy's limitations requires integrated approaches combining multiple technologies and strategies. Smart grid systems use sophisticated software to balance supply and demand in real-time, directing electricity where needed most efficiently. Complementary renewable sources can offset each other's intermittency—solar production peaks during summer days while wind often generates more power during winter nights. Hydrogen produced through electrolysis using excess renewable electricity offers a potential storage solution and clean fuel for transportation and industrial processes. Geothermal and hydroelectric power provide more consistent baseload electricity, stabilizing grids with high renewable penetration. Policy mechanisms also play crucial roles; countries like Germany and Denmark have achieved high renewable energy shares through supportive regulations, feed-in tariffs, and coordinated grid infrastructure investments. As technology continues advancing and societies recognize the urgent need to reduce greenhouse gas emissions, renewable energy is expected to dominate global electricity generation within the coming decades, fundamentally transforming energy systems that have relied on fossil fuels for over a century.`,

  paragraphs: [
    {
      id: 'para_a',
      label: 'A',
      content: 'The transition from fossil fuels to renewable energy sources represents one of the most critical challenges and opportunities of the 21st century. Unlike coal, oil, and natural gas, which release carbon dioxide accumulated over millions of years, renewable energy technologies harness naturally replenishing resources such as sunlight, wind, water flow, and geothermal heat. Solar photovoltaic technology has experienced dramatic cost reductions over the past decade, with prices falling more than 80% since 2010, making it now the cheapest source of electricity in many regions. Wind power has similarly become economically competitive, with modern turbines capable of generating electricity at costs comparable to or lower than conventional power plants. These economic shifts, combined with growing concerns about climate change and air pollution, have accelerated renewable energy adoption worldwide.',
      mainTopic: 'Renewable energy as a critical 21st-century transition, with solar and wind becoming economically competitive',
      keyDates: ['2010']
    },
    {
      id: 'para_b',
      label: 'B',
      content: 'Despite impressive progress, renewable energy integration faces significant technical and practical obstacles. The fundamental challenge lies in intermittency—solar panels generate electricity only during daylight hours, and wind turbines depend on wind availability, creating mismatches between energy generation and consumption patterns. This variability requires either backup power sources or energy storage systems, both of which add costs and complexity. Battery technology, particularly lithium-ion batteries, has improved substantially, but storing electricity at grid scale remains expensive and materials-intensive. Furthermore, renewable installations require considerably more land than fossil fuel plants for equivalent energy output. A coal power station might occupy several acres, while a solar farm producing comparable electricity could require hundreds of acres. This spatial footprint raises concerns about habitat disruption and competing land uses, particularly as agriculture and urban development already constrain available space.',
      mainTopic: 'Technical obstacles to renewable energy: intermittency, storage costs, and land requirements',
      keyDates: []
    },
    {
      id: 'para_c',
      label: 'C',
      content: 'Addressing renewable energy\'s limitations requires integrated approaches combining multiple technologies and strategies. Smart grid systems use sophisticated software to balance supply and demand in real-time, directing electricity where needed most efficiently. Complementary renewable sources can offset each other\'s intermittency—solar production peaks during summer days while wind often generates more power during winter nights. Hydrogen produced through electrolysis using excess renewable electricity offers a potential storage solution and clean fuel for transportation and industrial processes. Geothermal and hydroelectric power provide more consistent baseload electricity, stabilizing grids with high renewable penetration. Policy mechanisms also play crucial roles; countries like Germany and Denmark have achieved high renewable energy shares through supportive regulations, feed-in tariffs, and coordinated grid infrastructure investments. As technology continues advancing and societies recognize the urgent need to reduce greenhouse gas emissions, renewable energy is expected to dominate global electricity generation within the coming decades, fundamentally transforming energy systems that have relied on fossil fuels for over a century.',
      mainTopic: 'Integrated solutions for renewable energy challenges: smart grids, complementary sources, storage, and policy support',
      keyDates: []
    }
  ],

  vocabulary: [
    {
      id: 'vocab_1',
      word: 'replenishing',
      partOfSpeech: 'adjective',
      definition: 'being restored or renewed naturally',
      contextSentence: 'naturally replenishing resources',
      explanationInContext: 'Renewable resources like sunlight and wind are constantly renewed by nature - they don\'t run out',
      synonyms: ['renewable', 'restoring', 'renewing'],
      usage: 'Used to describe resources that are naturally restored',
      medicalConnection: null
    },
    {
      id: 'vocab_2',
      word: 'photovoltaic',
      partOfSpeech: 'adjective',
      definition: 'converting sunlight directly into electricity',
      contextSentence: 'Solar photovoltaic technology',
      explanationInContext: 'Technology that converts sunlight directly into electrical energy using solar cells',
      synonyms: ['solar power', 'solar energy'],
      usage: 'Technical term for solar electricity generation',
      medicalConnection: null
    },
    {
      id: 'vocab_3',
      word: 'dramatic',
      partOfSpeech: 'adjective',
      definition: 'very large or significant',
      contextSentence: 'dramatic cost reductions',
      explanationInContext: 'Very large and significant cost reductions - prices dropped a lot (over 80%)',
      synonyms: ['significant', 'substantial', 'major', 'striking'],
      usage: 'Used to emphasize something is very large or noticeable',
      medicalConnection: null
    },
    {
      id: 'vocab_4',
      word: 'intermittency',
      partOfSpeech: 'noun',
      definition: 'the quality of being irregular or not continuous',
      contextSentence: 'The fundamental challenge lies in intermittency',
      explanationInContext: 'Renewable energy is not continuous - solar only works during day, wind only when windy. This irregularity is the main problem.',
      synonyms: ['irregularity', 'variability', 'unpredictability'],
      usage: 'Technical term for irregular or non-continuous supply',
      medicalConnection: null
    },
    {
      id: 'vocab_5',
      word: 'variability',
      partOfSpeech: 'noun',
      definition: 'the quality of being changeable or inconsistent',
      contextSentence: 'This variability requires',
      explanationInContext: 'The changing, inconsistent nature of renewable energy (sometimes available, sometimes not)',
      synonyms: ['inconsistency', 'changeability', 'unpredictability'],
      usage: 'Used when something changes or is inconsistent',
      medicalConnection: null
    },
    {
      id: 'vocab_6',
      word: 'spatial footprint',
      partOfSpeech: 'noun',
      definition: 'the amount of physical space something occupies',
      contextSentence: 'This spatial footprint raises concerns',
      explanationInContext: 'The large amount of land that renewable energy installations need compared to fossil fuel plants',
      synonyms: ['land use', 'space requirement', 'physical footprint'],
      usage: 'Used to describe how much space something takes up',
      medicalConnection: null
    },
    {
      id: 'vocab_7',
      word: 'complementary',
      partOfSpeech: 'adjective',
      definition: 'combining well with something else to form a complete whole',
      contextSentence: 'Complementary renewable sources',
      explanationInContext: 'Different renewable sources that work well together - when one is low, the other is high',
      synonyms: ['supplementary', 'supporting', 'mutually beneficial'],
      usage: 'Used when things work well together',
      medicalConnection: null
    },
    {
      id: 'vocab_8',
      word: 'electrolysis',
      partOfSpeech: 'noun',
      definition: 'a process using electricity to split water into hydrogen and oxygen',
      contextSentence: 'Hydrogen produced through electrolysis',
      explanationInContext: 'A method of creating hydrogen fuel by using electricity to split water molecules',
      synonyms: ['electrochemical process'],
      usage: 'Scientific/technical term for splitting compounds using electricity',
      medicalConnection: null
    },
    {
      id: 'vocab_9',
      word: 'baseload',
      partOfSpeech: 'noun',
      definition: 'the minimum amount of power needed continuously',
      contextSentence: 'provide more consistent baseload electricity',
      explanationInContext: 'The steady, continuous power supply needed all the time (not just peak times)',
      synonyms: ['base power', 'minimum load', 'continuous supply'],
      usage: 'Energy industry term for continuous minimum power supply',
      medicalConnection: null
    },
    {
      id: 'vocab_10',
      word: 'penetration',
      partOfSpeech: 'noun',
      definition: 'the extent to which something is adopted or used',
      contextSentence: 'stabilizing grids with high renewable penetration',
      explanationInContext: 'When renewable energy makes up a large percentage of the energy supply',
      synonyms: ['adoption', 'integration', 'market share'],
      usage: 'Used to describe how widely something is adopted',
      medicalConnection: null
    }
  ],

  questions: [
    {
      id: 'q1',
      level: 1,
      type: 'vocabulary_context',
      difficulty: 'easy',
      paragraph: 'para_a',
      question: 'What does "replenishing" mean when describing renewable resources?',
      text: 'naturally replenishing resources',
      options: [
        {
          id: 'q1_a',
          text: 'Being restored or renewed naturally by natural processes',
          correct: true,
          explanation: 'Correct. "Replenishing" means being restored or renewed. Renewable resources like sunlight and wind are constantly renewed by nature - the sun keeps shining, wind keeps blowing. They don\'t get used up like fossil fuels, which are finite and deplete over time.'
        },
        {
          id: 'q1_b',
          text: 'Very expensive and costly to produce',
          correct: false,
          explanation: '"Replenishing" refers to being renewed and restored naturally, not cost or expense. The text actually says renewable energy has become cheaper (solar costs dropped 80%+), not expensive. The word describes the renewing nature of resources, not their economic cost.'
        },
        {
          id: 'q1_c',
          text: 'Running out quickly and becoming depleted',
          correct: false,
          explanation: 'This is the opposite meaning. "Replenishing" means being restored and renewed, so resources don\'t run out - they keep renewing naturally. Renewable resources are constantly replenished by natural processes, unlike finite fossil fuels that deplete.'
        },
        {
          id: 'q1_d',
          text: 'Only available at night or during specific times',
          correct: false,
          explanation: '"Replenishing" refers to the renewing and restoring nature of resources, not when they\'re available or their timing. Solar is available during daylight hours, wind can be available anytime depending on conditions, but the word describes the natural renewal process, not availability schedules.'
        }
      ],
      hint: 'Think about what happens to sunlight and wind - do they run out, or do they keep coming?',
      relatedVocabulary: ['vocab_1'],
      learningPoint: '"Replenishing" emphasizes sustainability - understanding this helps recognize why renewable resources are different from finite ones'
    },
    {
      id: 'q2',
      level: 1,
      type: 'vocabulary_context',
      difficulty: 'easy',
      paragraph: 'para_b',
      question: 'What does "intermittency" mean in the context of renewable energy?',
      text: 'The fundamental challenge lies in intermittency',
      options: [
        {
          id: 'q2_a',
          text: 'The quality of being irregular or not continuous in supply',
          correct: true,
          explanation: 'Correct. "Intermittency" means irregular or non-continuous supply. Solar only works during daylight hours, wind only when it\'s windy. This irregularity is the main challenge - energy isn\'t always available when needed, requiring storage systems or backup power sources to ensure continuous supply.'
        },
        {
          id: 'q2_b',
          text: 'Very high cost and expensive production',
          correct: false,
          explanation: '"Intermittency" refers to irregularity and non-continuity of supply, not cost or expense. The text discusses cost separately as a different challenge (expensive grid-scale storage). The word describes the unpredictable nature of energy availability, not economic factors.'
        },
        {
          id: 'q2_c',
          text: 'Constant and reliable supply that never stops',
          correct: false,
          explanation: 'This is the opposite meaning. "Intermittency" means irregular, unpredictable, and unreliable supply, not constant or reliable. The fundamental challenge is that renewable energy sources don\'t provide continuous power - they depend on weather conditions and time of day.'
        },
        {
          id: 'q2_d',
          text: 'Very efficient and highly productive energy generation',
          correct: false,
          explanation: '"Intermittency" refers to the irregular and non-continuous nature of supply, not efficiency or productivity. It\'s about availability and predictability of energy, not how well or efficiently the energy works when it is available. The challenge is timing, not performance.'
        }
      ],
      hint: 'The text says solar works "only during daylight hours" and wind "depends on wind availability." What does this tell you about regularity?',
      relatedVocabulary: ['vocab_4'],
      learningPoint: '"Intermittency" is a key challenge in renewable energy - understanding it helps recognize why storage and backup systems are needed'
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
          text: 'Fossil fuels are better than renewable energy',
          correct: false,
          explanation: 'The text describes renewable energy as a "critical" transition and shows it\'s becoming cheaper and more competitive, not that fossil fuels are better.'
        },
        {
          id: 'q3_b',
          text: 'The transition to renewable energy is critical with solar and wind becoming economically competitive',
          correct: true,
          explanation: 'This captures the paragraph\'s main points: (1) Transition is critical for the 21st century, (2) Renewable resources are naturally replenishing unlike finite fossil fuels, (3) Solar costs dropped dramatically (80%+), making it the cheapest source in many regions, (4) Wind is economically competitive, (5) Global adoption is accelerating. This covers the entire paragraph\'s purpose of showing renewable energy\'s importance and economic progress.'
        },
        {
          id: 'q3_c',
          text: 'Only solar energy matters and other sources are unimportant',
          correct: false,
          explanation: 'The paragraph discusses multiple renewable sources: sunlight, wind, water flow (hydroelectric), and geothermal heat. Solar and wind are highlighted as examples with dramatic cost reductions, but the paragraph presents renewable energy broadly, not just solar. Multiple sources are mentioned as part of the transition.'
        },
        {
          id: 'q3_d',
          text: 'Renewable energy is still very expensive and not affordable',
          correct: false,
          explanation: 'The text says solar is "now the cheapest source of electricity in many regions" and wind is "economically competitive," showing costs have decreased significantly (solar costs dropped 80%+). The paragraph emphasizes economic competitiveness and cost reductions, not high costs.'
        }
      ],
      hint: 'The paragraph introduces renewable energy as critical, shows cost reductions, and describes accelerating adoption. What is the overall message?',
      relatedVocabulary: ['vocab_1', 'vocab_2', 'vocab_3'],
      learningPoint: 'Main ideas often combine importance (critical) with progress (cost reductions, adoption) - here: critical transition with economic progress'
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
          text: 'Renewable energy has no problems',
          correct: false,
          explanation: 'The paragraph explicitly discusses "significant technical and practical obstacles" and "fundamental challenge," showing there are problems.'
        },
        {
          id: 'q4_b',
          text: 'Renewable energy faces obstacles including intermittency requiring storage and large land requirements',
          correct: true,
          explanation: 'This captures the paragraph\'s themes: (1) Obstacles exist despite impressive progress, (2) Fundamental challenge is intermittency (solar only during daylight, wind depends on availability), (3) Expensive grid-scale storage needed to address intermittency, (4) Large land requirements (solar farms need hundreds of acres vs. coal\'s several acres), (5) Environmental concerns about land use. This covers all major obstacles mentioned.'
        },
        {
          id: 'q4_c',
          text: 'Only cost is a problem and all other issues are solved',
          correct: false,
          explanation: 'The paragraph discusses multiple obstacles: intermittency (the fundamental challenge), expensive grid-scale storage, AND large land requirements that raise environmental concerns. Cost is one issue among several, not the only problem. The text presents multiple technical and practical obstacles.'
        },
        {
          id: 'q4_d',
          text: 'Renewable energy takes less land than fossil fuel installations',
          correct: false,
          explanation: 'The text explicitly says renewable installations "require considerably more land" - a solar farm needs "hundreds of acres" compared to a coal plant\'s "several acres." This is presented as one of the obstacles, not an advantage. Land requirements are a significant challenge for renewable energy.'
        }
      ],
      hint: 'The paragraph starts with "Despite impressive progress" and then lists obstacles. What are the main challenges?',
      relatedVocabulary: ['vocab_4', 'vocab_5', 'vocab_6'],
      learningPoint: 'Main themes often balance progress with challenges - here: impressive progress but significant obstacles remain'
    },
    {
      id: 'q5',
      level: 3,
      type: 'inference',
      difficulty: 'hard',
      paragraph: 'para_b',
      question: 'Why does the author mention that a solar farm requires "hundreds of acres" compared to coal\'s "several acres"?',
      options: [
        {
          id: 'q5_a',
          text: 'To highlight that land requirements are a significant obstacle raising environmental concerns',
          correct: true,
          explanation: 'Correct. By showing the dramatic difference (hundreds vs. several acres), the author emphasizes that land use is a major concern. This connects to the following sentence about "habitat disruption and competing land uses," showing why this matters environmentally and practically - renewable energy installations require much more land, which can disrupt habitats and compete with agriculture and other land uses.'
        },
        {
          id: 'q5_b',
          text: 'To show that solar energy is better and superior to coal power',
          correct: false,
          explanation: 'The comparison shows solar needs much more land (hundreds of acres vs. several acres), which is presented as a problem and obstacle, not an advantage or superiority. The author is highlighting a significant challenge for renewable energy, not arguing that solar is better.'
        },
        {
          id: 'q5_c',
          text: 'To explain how solar panels work and generate electricity',
          correct: false,
          explanation: 'The text doesn\'t explain how solar panels work or the technology behind electricity generation - it compares land requirements to show a challenge and obstacle. The comparison is about space needed, not about the technical process of solar energy generation.'
        },
        {
          id: 'q5_d',
          text: 'To show that coal power is better and should be preferred',
          correct: false,
          explanation: 'The author isn\'t arguing coal is better or should be preferred - they\'re presenting obstacles and challenges to renewable energy that need to be addressed. The comparison shows a significant challenge (large land requirements) that renewable energy faces, not an argument for using coal instead.'
        }
      ],
      hint: 'The sentence immediately after mentions "habitat disruption and competing land uses." What does this tell you about why the land comparison is important?',
      relatedVocabulary: ['vocab_6'],
      learningPoint: 'Authors use specific comparisons to emphasize obstacles - here: dramatic land difference highlights environmental and practical concerns'
    },
    {
      id: 'q6',
      level: 3,
      type: 'inference',
      difficulty: 'hard',
      paragraph: 'para_c',
      question: 'What does the author imply by saying complementary sources "can offset each other\'s intermittency"?',
      options: [
        {
          id: 'q6_a',
          text: 'Different renewable sources can work together to provide more consistent energy reducing intermittency',
          correct: true,
          explanation: 'Correct. "Offset" means to balance or compensate. The author shows that solar peaks in summer days while wind peaks in winter nights - they complement each other. When solar is low (night/winter), wind might be high, and vice versa. This creates a more reliable combined system than either source alone, reducing the intermittency problem.'
        },
        {
          id: 'q6_b',
          text: 'Only one renewable source should be used at a time separately',
          correct: false,
          explanation: '"Offset" means they work together and complement each other, not separately or one at a time. The text describes combining sources (solar and wind together) to create a more reliable system, not using them individually or sequentially.'
        },
        {
          id: 'q6_c',
          text: 'Renewable sources always work at the same time simultaneously',
          correct: false,
          explanation: 'The text shows they work at different times (solar peaks in summer days, wind peaks in winter nights), which is why they can offset each other - when one is low or unavailable, the other can be high or available. Their different timing patterns are what make them complementary.'
        },
        {
          id: 'q6_d',
          text: 'Complementary sources make intermittency worse and more problematic',
          correct: false,
          explanation: '"Offset" means to reduce, balance, or compensate for intermittency, not worsen it. The text presents complementary sources working together as a solution to intermittency, showing how different sources can balance each other\'s weaknesses, not make the problem worse.'
        }
      ],
      hint: 'The text says solar peaks in "summer days" while wind peaks in "winter nights." What does this tell you about how they work together?',
      relatedVocabulary: ['vocab_7'],
      learningPoint: '"Offset" means balancing - understanding this helps recognize how different solutions can work together to solve problems'
    },
    {
      id: 'q7',
      level: 4,
      type: 'synthesis',
      difficulty: 'very_hard',
      paragraph: null,
      question: 'How does the author develop the argument about renewable energy across all three paragraphs?',
      options: [
        {
          id: 'q7_a',
          text: 'From opportunity and progress to challenges to solutions showing a balanced path forward',
          correct: true,
          explanation: 'Perfect synthesis. Paragraph A: Establishes renewable energy as critical opportunity with economic progress (cost reductions, competitiveness, accelerating adoption). Paragraph B: Acknowledges significant obstacles (intermittency, expensive storage, large land requirements, environmental concerns). Paragraph C: Presents integrated solutions (smart grids, complementary sources, storage technologies, policy support). This builds: opportunity → challenges → solutions, showing a realistic but optimistic path forward.'
        },
        {
          id: 'q7_b',
          text: 'From problems to more problems to even more problems without solutions',
          correct: false,
          explanation: 'The text shows progress and opportunity (A with cost reductions and competitiveness), acknowledges challenges (B with obstacles), but then presents solutions (C with integrated approaches, smart grids, policy). It\'s not just problems - it\'s a balanced assessment with a path forward showing how challenges can be addressed.'
        },
        {
          id: 'q7_c',
          text: 'From past historical developments to present situation to future predictions',
          correct: false,
          explanation: 'While there\'s a future element in paragraph C, the main progression is: opportunity/progress (A) → challenges/obstacles (B) → solutions/path forward (C), not a chronological progression from past to present to future. The structure is about different aspects of renewable energy, not time periods.'
        },
        {
          id: 'q7_d',
          text: 'From proven scientific solutions to unproven speculative claims',
          correct: false,
          explanation: 'The text presents documented progress (A with real cost reductions and competitiveness), real challenges (B with actual obstacles), and practical solutions (C with integrated approaches, smart grids, storage technologies). It\'s a balanced assessment with evidence-based claims, not a progression from proven to unproven.'
        }
      ],
      hint: 'Look at what each paragraph does: A shows opportunity/progress, B shows challenges, C shows solutions. How does this build a complete argument?',
      relatedVocabulary: ['vocab_1', 'vocab_3', 'vocab_4', 'vocab_6', 'vocab_7', 'vocab_8', 'vocab_9', 'vocab_10'],
      learningPoint: 'Effective arguments often follow: opportunity/progress → challenges → solutions - recognizing this structure helps understand the complete message'
    },
    {
      id: 'q8',
      level: 4,
      type: 'synthesis',
      difficulty: 'very_hard',
      paragraph: null,
      question: 'What is the author\'s overall argument about renewable energy?',
      options: [
        {
          id: 'q8_a',
          text: 'Renewable energy is a critical opportunity with economic progress facing real challenges but solutions exist',
          correct: true,
          explanation: 'This captures the complete argument: (1) Critical opportunity with significant economic progress (cost reductions, competitiveness, accelerating adoption) (A), (2) Real technical challenges exist (intermittency, storage costs, land requirements) (B), (3) Integrated solutions available (smart grids, complementary sources, storage technologies) (C), (4) Policy support is crucial for success (C), (5) Expected to dominate future electricity generation (C). The author balances realism about challenges with optimism about solutions and future potential.'
        },
        {
          id: 'q8_b',
          text: 'Renewable energy is impossible and will never work or succeed',
          correct: false,
          explanation: 'The text shows significant economic progress (cost reductions, competitiveness), presents practical solutions (smart grids, storage, complementary sources), and predicts renewable energy will "dominate global electricity generation," showing it\'s not impossible and is expected to succeed in the future.'
        },
        {
          id: 'q8_c',
          text: 'Only solar and wind energy sources matter and are important',
          correct: false,
          explanation: 'The text discusses multiple renewable sources: solar, wind, water flow (hydroelectric), geothermal heat, and hydrogen. While solar and wind are highlighted as examples with dramatic cost reductions, the paragraph presents renewable energy broadly, not limited to just solar and wind.'
        },
        {
          id: 'q8_d',
          text: 'Renewable energy has no challenges or obstacles to overcome',
          correct: false,
          explanation: 'Paragraph B explicitly discusses "significant technical and practical obstacles" and "fundamental challenge" of intermittency, along with expensive storage and large land requirements. The text clearly acknowledges multiple challenges that need to be addressed, not that there are no challenges.'
        }
      ],
      hint: 'Combine the opportunity (A), challenges (B), and solutions/future (C). What is the author\'s overall message about renewable energy\'s potential?',
      relatedVocabulary: ['vocab_1', 'vocab_3', 'vocab_4', 'vocab_6', 'vocab_7', 'vocab_8', 'vocab_9', 'vocab_10'],
      learningPoint: 'Overall arguments often balance opportunity with realism - here: critical opportunity with challenges, but solutions and future dominance expected'
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

