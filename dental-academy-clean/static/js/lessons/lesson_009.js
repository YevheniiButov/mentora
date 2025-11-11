// Reading Comprehension Lesson 009: The Science of Sleep
export const lesson009 = {
  id: 'lesson_009',
  title: 'The Science of Sleep',
  language: 'English',
  professionContext: 'Medical professionals reading scientific content',
  estimatedTime: 15,
  imageUrl: '/static/images/passages/sleep-science.png',
  
  text: `A Sleep represents a fundamental biological necessity that occupies approximately one-third of human life, yet its precise functions and mechanisms remained largely mysterious until recent decades. Contemporary sleep research has revealed that far from being a passive state of rest, sleep involves complex active processes that are essential for physical health, cognitive function, and emotional regulation. During sleep, the brain cycles through distinct stages, each characterized by different patterns of electrical activity and serving specific purposes. Non-rapid eye movement (NREM) sleep, which comprises about 75% of total sleep time, appears particularly important for physical restoration and memory consolidation, while rapid eye movement (REM) sleep, marked by vivid dreaming and intense brain activity, plays crucial roles in emotional processing and creative problem-solving.

B The consequences of inadequate sleep extend far beyond simple fatigue, affecting virtually every physiological system. Chronic sleep deprivation has been linked to increased risk of cardiovascular disease, diabetes, obesity, and weakened immune function. Even moderate sleep restriction—sleeping six hours nightly instead of the recommended seven to nine—produces measurable cognitive impairments equivalent to being legally intoxicated. Sleep-deprived individuals demonstrate reduced attention spans, impaired decision-making abilities, and decreased memory formation. Furthermore, insufficient sleep disrupts hormonal balance, increasing production of ghrelin (which stimulates appetite) while decreasing leptin (which signals satiety), thereby promoting weight gain. Studies of shift workers, who frequently experience disrupted sleep schedules, reveal elevated rates of numerous health conditions, suggesting that irregular sleep patterns may be particularly harmful. The accumulation of these effects has led some researchers to describe modern society's sleep patterns as a public health crisis.

C Despite growing awareness of sleep's importance, understanding individual sleep requirements remains complex. While general guidelines recommend seven to nine hours for adults, optimal sleep duration varies based on age, genetics, lifestyle, and overall health. Some individuals function well on relatively little sleep—genuine "short sleepers" who naturally require only five to six hours without apparent negative effects—though such people represent a small minority of the population, perhaps 1-3%. More commonly, people mistakenly believe they have adapted to insufficient sleep when they have actually experienced a deterioration in performance that they no longer recognize. Improving sleep quality involves multiple strategies: maintaining consistent sleep schedules, avoiding screens before bedtime (as blue light suppresses melatonin production), creating cool, dark sleeping environments, and managing stress through relaxation techniques. As neuroscience continues advancing, researchers hope to develop more targeted interventions for sleep disorders and better understand sleep's essential but still partly enigmatic functions.`,

  paragraphs: [
    {
      id: 'para_a',
      label: 'A',
      content: 'Sleep represents a fundamental biological necessity that occupies approximately one-third of human life, yet its precise functions and mechanisms remained largely mysterious until recent decades. Contemporary sleep research has revealed that far from being a passive state of rest, sleep involves complex active processes that are essential for physical health, cognitive function, and emotional regulation. During sleep, the brain cycles through distinct stages, each characterized by different patterns of electrical activity and serving specific purposes. Non-rapid eye movement (NREM) sleep, which comprises about 75% of total sleep time, appears particularly important for physical restoration and memory consolidation, while rapid eye movement (REM) sleep, marked by vivid dreaming and intense brain activity, plays crucial roles in emotional processing and creative problem-solving.',
      mainTopic: 'Sleep as an active, complex process with distinct stages (NREM and REM) serving different essential functions',
      keyDates: []
    },
    {
      id: 'para_b',
      label: 'B',
      content: 'The consequences of inadequate sleep extend far beyond simple fatigue, affecting virtually every physiological system. Chronic sleep deprivation has been linked to increased risk of cardiovascular disease, diabetes, obesity, and weakened immune function. Even moderate sleep restriction—sleeping six hours nightly instead of the recommended seven to nine—produces measurable cognitive impairments equivalent to being legally intoxicated. Sleep-deprived individuals demonstrate reduced attention spans, impaired decision-making abilities, and decreased memory formation. Furthermore, insufficient sleep disrupts hormonal balance, increasing production of ghrelin (which stimulates appetite) while decreasing leptin (which signals satiety), thereby promoting weight gain. Studies of shift workers, who frequently experience disrupted sleep schedules, reveal elevated rates of numerous health conditions, suggesting that irregular sleep patterns may be particularly harmful. The accumulation of these effects has led some researchers to describe modern society\'s sleep patterns as a public health crisis.',
      mainTopic: 'Widespread health consequences of inadequate sleep affecting multiple body systems and cognitive function',
      keyDates: []
    },
    {
      id: 'para_c',
      label: 'C',
      content: 'Despite growing awareness of sleep\'s importance, understanding individual sleep requirements remains complex. While general guidelines recommend seven to nine hours for adults, optimal sleep duration varies based on age, genetics, lifestyle, and overall health. Some individuals function well on relatively little sleep—genuine "short sleepers" who naturally require only five to six hours without apparent negative effects—though such people represent a small minority of the population, perhaps 1-3%. More commonly, people mistakenly believe they have adapted to insufficient sleep when they have actually experienced a deterioration in performance that they no longer recognize. Improving sleep quality involves multiple strategies: maintaining consistent sleep schedules, avoiding screens before bedtime (as blue light suppresses melatonin production), creating cool, dark sleeping environments, and managing stress through relaxation techniques. As neuroscience continues advancing, researchers hope to develop more targeted interventions for sleep disorders and better understand sleep\'s essential but still partly enigmatic functions.',
      mainTopic: 'Individual variation in sleep needs and strategies for improving sleep quality, with ongoing research',
      keyDates: []
    }
  ],

  vocabulary: [
    {
      id: 'vocab_1',
      word: 'fundamental',
      partOfSpeech: 'adjective',
      definition: 'basic and essential',
      contextSentence: 'a fundamental biological necessity',
      explanationInContext: 'Sleep is a basic, essential biological need - we cannot survive without it',
      synonyms: ['essential', 'basic', 'core', 'vital'],
      usage: 'Used to describe something that is absolutely necessary',
      medicalConnection: 'Common in medical contexts - "fundamental" biological processes'
    },
    {
      id: 'vocab_2',
      word: 'consolidation',
      partOfSpeech: 'noun',
      definition: 'the process of making something stronger or more solid',
      contextSentence: 'memory consolidation',
      explanationInContext: 'During sleep, memories are strengthened and made more permanent in the brain',
      synonyms: ['strengthening', 'reinforcement', 'solidification'],
      usage: 'Used when something is made stronger or more permanent',
      medicalConnection: 'Medical/neuroscience term - memory consolidation is a key brain process'
    },
    {
      id: 'vocab_3',
      word: 'deprivation',
      partOfSpeech: 'noun',
      definition: 'the state of not having something that is needed',
      contextSentence: 'Chronic sleep deprivation',
      explanationInContext: 'Not getting enough sleep over a long period of time',
      synonyms: ['lack', 'absence', 'deficiency'],
      usage: 'Used when something essential is missing',
      medicalConnection: 'Medical term - sleep deprivation, oxygen deprivation'
    },
    {
      id: 'vocab_4',
      word: 'cardiovascular',
      partOfSpeech: 'adjective',
      definition: 'relating to the heart and blood vessels',
      contextSentence: 'cardiovascular disease',
      explanationInContext: 'Diseases affecting the heart and circulatory system',
      synonyms: ['heart-related', 'circulatory'],
      usage: 'Medical term for heart and blood vessel system',
      medicalConnection: 'Direct medical term - cardiovascular system, cardiovascular disease'
    },
    {
      id: 'vocab_5',
      word: 'impairments',
      partOfSpeech: 'noun',
      definition: 'reductions in ability or function',
      contextSentence: 'measurable cognitive impairments',
      explanationInContext: 'Reduced cognitive abilities - thinking, memory, attention are worse',
      synonyms: ['deficits', 'reductions', 'decreases'],
      usage: 'Used to describe reduced function or ability',
      medicalConnection: 'Medical term - cognitive impairments, visual impairments'
    },
    {
      id: 'vocab_6',
      word: 'intoxicated',
      partOfSpeech: 'adjective',
      definition: 'under the influence of alcohol or drugs',
      contextSentence: 'equivalent to being legally intoxicated',
      explanationInContext: 'Sleep deprivation makes cognitive function as bad as being drunk',
      synonyms: ['drunk', 'under the influence'],
      usage: 'Legal/medical term for being affected by substances',
      medicalConnection: 'Medical/legal term - intoxication levels'
    },
    {
      id: 'vocab_7',
      word: 'ghrelin',
      partOfSpeech: 'noun',
      definition: 'a hormone that stimulates appetite',
      contextSentence: 'increasing production of ghrelin (which stimulates appetite)',
      explanationInContext: 'A hormone that makes you feel hungry - sleep deprivation increases it',
      synonyms: ['hunger hormone'],
      usage: 'Medical/scientific term for a specific hormone',
      medicalConnection: 'Direct medical term - hormone involved in appetite regulation'
    },
    {
      id: 'vocab_8',
      word: 'leptin',
      partOfSpeech: 'noun',
      definition: 'a hormone that signals fullness or satiety',
      contextSentence: 'decreasing leptin (which signals satiety)',
      explanationInContext: 'A hormone that tells your brain you\'re full - sleep deprivation decreases it',
      synonyms: ['satiety hormone'],
      usage: 'Medical/scientific term for a specific hormone',
      medicalConnection: 'Direct medical term - hormone involved in appetite and metabolism'
    },
    {
      id: 'vocab_9',
      word: 'melatonin',
      partOfSpeech: 'noun',
      definition: 'a hormone that regulates sleep-wake cycles',
      contextSentence: 'blue light suppresses melatonin production',
      explanationInContext: 'A hormone that helps you sleep - blue light from screens reduces it, making sleep harder',
      synonyms: ['sleep hormone'],
      usage: 'Medical/scientific term for a sleep-regulating hormone',
      medicalConnection: 'Direct medical term - hormone that regulates circadian rhythms and sleep'
    },
    {
      id: 'vocab_10',
      word: 'enigmatic',
      partOfSpeech: 'adjective',
      definition: 'mysterious or difficult to understand',
      contextSentence: 'still partly enigmatic functions',
      explanationInContext: 'Some functions of sleep are still mysterious and not fully understood',
      synonyms: ['mysterious', 'puzzling', 'unclear'],
      usage: 'Used to describe something that is mysterious or not fully understood',
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
      question: 'What does "consolidation" mean in the context of memory?',
      text: 'memory consolidation',
      options: [
        {
          id: 'q1_a',
          text: 'The process of making memories stronger and more permanent',
          correct: true,
          explanation: 'Correct. "Consolidation" means making something stronger or more solid. During sleep, memories are strengthened and made more permanent in the brain through neural processes - this is why sleep is important for learning and memory retention.'
        },
        {
          id: 'q1_b',
          text: 'Forgetting memories and losing information',
          correct: false,
          explanation: 'This is the opposite meaning. "Consolidation" means strengthening and stabilizing memories, not forgetting or losing them. The process makes memories more durable and accessible, not weaker or forgotten.'
        },
        {
          id: 'q1_c',
          text: 'Creating new memories and forming new information',
          correct: false,
          explanation: 'Consolidation happens to existing memories that were formed during wakefulness (making them stronger and more permanent), not creating new ones. New memories are initially formed during wakefulness, then consolidated during sleep.'
        },
        {
          id: 'q1_d',
          text: 'Deleting old memories and removing information',
          correct: false,
          explanation: '"Consolidation" means strengthening and stabilizing memories, not deleting or removing them. It makes memories more permanent and durable in the brain, not eliminates them. The process enhances memory retention, not deletion.'
        }
      ],
      hint: 'Think about what happens when something is "consolidated" - does it get stronger or weaker?',
      relatedVocabulary: ['vocab_2'],
      learningPoint: '"Consolidation" is a key neuroscience concept - understanding it helps recognize why sleep is important for learning'
    },
    {
      id: 'q2',
      level: 1,
      type: 'vocabulary_context',
      difficulty: 'easy',
      paragraph: 'para_b',
      question: 'What does "ghrelin" do in the body?',
      text: 'increasing production of ghrelin (which stimulates appetite)',
      options: [
        {
          id: 'q2_a',
          text: 'A hormone that makes you feel hungry and stimulates appetite',
          correct: true,
          explanation: 'Correct. Ghrelin is a hormone that stimulates appetite - it makes you feel hungry. Sleep deprivation increases ghrelin production, which is why lack of sleep can lead to increased appetite and weight gain. This hormonal disruption is one of the ways inadequate sleep affects metabolism.'
        },
        {
          id: 'q2_b',
          text: 'A hormone that makes you feel full and suppresses appetite',
          correct: false,
          explanation: 'That\'s leptin, not ghrelin. Ghrelin does the opposite - it stimulates appetite and makes you feel hungry, not full. The text specifically says ghrelin "stimulates appetite," which is the opposite of making you feel full.'
        },
        {
          id: 'q2_c',
          text: 'A type of sleep disorder or sleep-related condition',
          correct: false,
          explanation: 'Ghrelin is a hormone involved in appetite regulation, not a sleep disorder or condition. The text discusses how sleep deprivation affects ghrelin production, showing it\'s a hormone that responds to sleep, not a sleep disorder itself.'
        },
        {
          id: 'q2_d',
          text: 'A measurement of sleep quality and sleep duration',
          correct: false,
          explanation: 'Ghrelin is a hormone that affects appetite and metabolism, not a measurement or metric of sleep. The text discusses how sleep affects ghrelin production (inadequate sleep increases it), but ghrelin itself is a hormone, not a measurement tool.'
        }
      ],
      hint: 'The text says ghrelin "stimulates appetite." What does this tell you about what it does?',
      relatedVocabulary: ['vocab_7'],
      learningPoint: 'Understanding hormones like ghrelin helps explain how sleep affects appetite and weight'
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
          text: 'Sleep is a waste of time',
          correct: false,
          explanation: 'The text describes sleep as a "fundamental biological necessity" with "essential" functions, clearly showing it\'s important, not wasteful.'
        },
        {
          id: 'q3_b',
          text: 'Sleep is an active complex process with distinct stages serving essential functions',
          correct: true,
          explanation: 'This captures the paragraph\'s main points: (1) Sleep is fundamental biological necessity that was mysterious, (2) It\'s an active process (not passive rest), (3) Has distinct stages (NREM and REM) with different purposes, (4) NREM for physical restoration and memory consolidation, (5) REM for emotional processing and creativity. This covers the entire paragraph\'s purpose of showing sleep as an active, essential process with important functions.'
        },
        {
          id: 'q3_c',
          text: 'Only REM sleep matters and NREM is unimportant',
          correct: false,
          explanation: 'The text discusses both NREM (75% of sleep time, essential for physical restoration and memory consolidation) and REM (important for emotional processing and creativity), showing both stages are important for different essential functions. The paragraph emphasizes the importance of both stages, not just one.'
        },
        {
          id: 'q3_d',
          text: 'Sleep is completely understood and fully researched',
          correct: false,
          explanation: 'The text says sleep\'s functions "remained largely mysterious until recent decades" and ends with "still partly enigmatic," showing it\'s not fully understood or completely researched. While significant progress has been made, sleep remains partially mysterious.'
        }
      ],
      hint: 'The paragraph introduces sleep as fundamental, describes it as active (not passive), and explains the different stages. What is the overall message?',
      relatedVocabulary: ['vocab_1', 'vocab_2'],
      learningPoint: 'Main ideas often correct misconceptions - here: sleep is active, not passive, with important functions'
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
          text: 'Lack of sleep only causes tiredness',
          correct: false,
          explanation: 'The text says consequences "extend far beyond simple fatigue" and affect "virtually every physiological system," showing much more than just tiredness.'
        },
        {
          id: 'q4_b',
          text: 'Inadequate sleep has widespread serious consequences affecting multiple body systems and cognitive function',
          correct: true,
          explanation: 'This captures the paragraph\'s themes: (1) Consequences extend far beyond simple fatigue, (2) Multiple health risks affecting virtually every physiological system (cardiovascular disease, diabetes, obesity, weakened immune function), (3) Cognitive impairments equivalent to legal intoxication, (4) Hormonal disruption (increased ghrelin, decreased leptin), (5) Described as a public health crisis. This covers all major consequences showing the serious, widespread impact of inadequate sleep.'
        },
        {
          id: 'q4_c',
          text: 'Only shift workers are affected by sleep problems',
          correct: false,
          explanation: 'Shift workers are mentioned as one example of people with disrupted sleep patterns, but the paragraph discusses effects on everyone with inadequate sleep, not just shift workers. The consequences described (cardiovascular, immune, cognitive, hormonal) apply to anyone with insufficient sleep, not just specific groups.'
        },
        {
          id: 'q4_d',
          text: 'Sleep does not affect health or body functions',
          correct: false,
          explanation: 'The paragraph provides extensive evidence of health effects affecting "virtually every physiological system," including cardiovascular, immune, hormonal, and cognitive functions. The text clearly shows sleep significantly affects health, with inadequate sleep described as a public health crisis.'
        }
      ],
      hint: 'The paragraph lists multiple consequences. What do they all show about the seriousness of inadequate sleep?',
      relatedVocabulary: ['vocab_3', 'vocab_4', 'vocab_5', 'vocab_6', 'vocab_7', 'vocab_8'],
      learningPoint: 'Main themes often emphasize seriousness - here: inadequate sleep affects everything, described as a crisis'
    },
    {
      id: 'q5',
      level: 3,
      type: 'inference',
      difficulty: 'hard',
      paragraph: 'para_b',
      question: 'Why does the author compare sleep deprivation to being "legally intoxicated"?',
      options: [
        {
          id: 'q5_a',
          text: 'To emphasize the severity of cognitive impairment by comparing it to a well-known dangerous state',
          correct: true,
          explanation: 'Correct. By comparing sleep deprivation to legal intoxication (being drunk), the author uses a familiar, serious comparison to emphasize how bad cognitive impairment can be. Most people understand that being drunk impairs judgment and reaction time - comparing sleep loss to this shows it\'s equally dangerous for cognitive function.'
        },
        {
          id: 'q5_b',
          text: 'To show that sleep and alcohol are exactly the same thing',
          correct: false,
          explanation: 'The comparison is about cognitive effects and impairment levels, not that sleep and alcohol are the same thing. The author is using a familiar comparison (intoxication) to emphasize the severity of cognitive impairment from sleep loss, not equating the substances themselves.'
        },
        {
          id: 'q5_c',
          text: 'To criticize people who drink alcohol and consume alcohol',
          correct: false,
          explanation: 'The author isn\'t criticizing drinking or alcohol consumption - they\'re using intoxication as a familiar, well-understood comparison to show how serious and dangerous cognitive impairment from sleep deprivation can be. The comparison helps readers understand severity, not criticize behavior.'
        },
        {
          id: 'q5_d',
          text: 'To explain how alcohol affects sleep quality and sleep patterns',
          correct: false,
          explanation: 'The text doesn\'t discuss how alcohol affects sleep quality or patterns. The comparison is about cognitive impairment levels - showing that sleep-deprived people have cognitive function equivalent to legally intoxicated people, not about alcohol\'s effects on sleep itself.'
        }
      ],
      hint: 'Why would an author compare something to a well-known dangerous state? What does this comparison help readers understand?',
      relatedVocabulary: ['vocab_5', 'vocab_6'],
      learningPoint: 'Authors use familiar comparisons to emphasize severity - here: comparing sleep loss to intoxication shows how serious it is'
    },
    {
      id: 'q6',
      level: 3,
      type: 'inference',
      difficulty: 'hard',
      paragraph: 'para_c',
      question: 'What does the author imply by saying people "mistakenly believe they have adapted to insufficient sleep when they have actually experienced a deterioration in performance that they no longer recognize"?',
      options: [
        {
          id: 'q6_a',
          text: 'People think they are fine with less sleep but their performance has actually gotten worse',
          correct: true,
          explanation: 'Correct. The author suggests that when people get used to less sleep, they think they\'ve adapted (gotten used to it and are fine), but actually their performance has deteriorated (gotten worse). Because the decline happens slowly over time, people don\'t notice it - they think they\'re functioning normally when they\'re actually performing worse than they would with adequate sleep.'
        },
        {
          id: 'q6_b',
          text: 'Everyone adapts well to less sleep and performance improves',
          correct: false,
          explanation: 'The text says people "mistakenly believe" they\'ve adapted, and describes "deterioration in performance," showing adaptation isn\'t real - performance actually gets worse, not better. The belief in adaptation is mistaken, not accurate.'
        },
        {
          id: 'q6_c',
          text: 'People always notice immediately when their performance declines',
          correct: false,
          explanation: 'The text says people "no longer recognize" the deterioration and "mistakenly believe they have adapted," showing they don\'t notice the decline. The gradual nature of the decline makes it imperceptible to people experiencing it.'
        },
        {
          id: 'q6_d',
          text: 'Less sleep improves performance and makes people more productive',
          correct: false,
          explanation: 'The text describes "deterioration in performance," showing less sleep makes performance worse, not better. The paragraph emphasizes the negative consequences of inadequate sleep, not benefits.'
        }
      ],
      hint: 'What does "deterioration" mean? What does "they no longer recognize" tell you about whether people notice the decline?',
      relatedVocabulary: ['vocab_5'],
      learningPoint: 'Understanding gradual decline helps recognize why people might not notice sleep deprivation effects'
    },
    {
      id: 'q7',
      level: 4,
      type: 'synthesis',
      difficulty: 'very_hard',
      paragraph: null,
      question: 'How does the author develop the argument about sleep across all three paragraphs?',
      options: [
        {
          id: 'q7_a',
          text: 'From importance and mechanisms to consequences of inadequate sleep to individual variation and strategies',
          correct: true,
          explanation: 'Perfect synthesis. Paragraph A: Establishes sleep\'s importance as fundamental biological necessity and explains it\'s an active process with distinct stages (NREM and REM) serving different essential functions. Paragraph B: Shows serious consequences of inadequate sleep (widespread health risks, cognitive impairments equivalent to intoxication, hormonal disruption, public health crisis). Paragraph C: Discusses individual variation in needs and provides strategies for improvement, acknowledging complexity. This builds: what sleep is → why it matters (consequences of lack) → how to improve it.'
        },
        {
          id: 'q7_b',
          text: 'From problems to solutions to even more problems without resolution',
          correct: false,
          explanation: 'The text shows importance and mechanisms (A), consequences of inadequate sleep (B), and solutions/strategies for improvement (C). It\'s not just problems - it\'s a balanced assessment with practical solutions and strategies, showing a path forward despite challenges.'
        },
        {
          id: 'q7_c',
          text: 'From simple basic explanations to increasingly complex and detailed descriptions',
          correct: false,
          explanation: 'While complexity increases somewhat, the main progression is: what sleep is and why it\'s important (A) → consequences of inadequate sleep (B) → how to improve it with individual variation (C), not just a progression from simple to complex. The structure is about different aspects of sleep, not complexity levels.'
        },
        {
          id: 'q7_d',
          text: 'From proven scientific facts to unproven speculative claims',
          correct: false,
          explanation: 'The text presents research-based information throughout (active process, distinct stages, health consequences, cognitive effects). While some functions are "enigmatic" or "partly mysterious," the progression isn\'t from proven to unproven - it\'s about building understanding across different aspects of sleep.'
        }
      ],
      hint: 'Look at what each paragraph does: A explains what sleep is, B shows what happens without it, C discusses how to improve it. How does this build a complete argument?',
      relatedVocabulary: ['vocab_1', 'vocab_2', 'vocab_3', 'vocab_4', 'vocab_5', 'vocab_7', 'vocab_8', 'vocab_9', 'vocab_10'],
      learningPoint: 'Effective health arguments often follow: what it is → why it matters (consequences) → how to improve - recognizing this structure helps understand complete health messages'
    },
    {
      id: 'q8',
      level: 4,
      type: 'synthesis',
      difficulty: 'very_hard',
      paragraph: null,
      question: 'What is the author\'s overall argument about sleep?',
      options: [
        {
          id: 'q8_a',
          text: 'Sleep is a fundamental active process essential for health with inadequate sleep causing serious consequences but strategies exist',
          correct: true,
          explanation: 'This captures the complete argument: (1) Sleep is fundamental biological necessity and active process (A), (2) Essential for health with distinct stages serving different functions (A), (3) Inadequate sleep has serious widespread consequences affecting virtually every physiological system (B), (4) Described as public health crisis (B), (5) Individual needs vary based on multiple factors (C), (6) Strategies exist for improvement despite complexity (C). The author combines scientific explanation with practical implications.'
        },
        {
          id: 'q8_b',
          text: 'Sleep is not important and has no effect on health',
          correct: false,
          explanation: 'The text describes sleep as "fundamental biological necessity" with "essential" functions and shows serious widespread consequences of inadequate sleep affecting virtually every physiological system, clearly showing its critical importance for health.'
        },
        {
          id: 'q8_c',
          text: 'Everyone needs exactly the same amount of sleep without variation',
          correct: false,
          explanation: 'Paragraph C explicitly states "optimal sleep duration varies based on age, genetics, lifestyle, and overall health," showing significant individual variation. The text emphasizes that needs are complex and vary, not uniform.'
        },
        {
          id: 'q8_d',
          text: 'Sleep only affects tiredness and fatigue levels',
          correct: false,
          explanation: 'The text shows sleep affects "virtually every physiological system" including cardiovascular disease, diabetes, obesity, immune function, hormonal regulation, and cognitive function equivalent to legal intoxication - much more than just tiredness or fatigue.'
        }
      ],
      hint: 'Combine the importance (A), consequences (B), and individual variation/strategies (C). What is the author\'s overall message about sleep?',
      relatedVocabulary: ['vocab_1', 'vocab_2', 'vocab_3', 'vocab_4', 'vocab_5', 'vocab_7', 'vocab_8', 'vocab_9', 'vocab_10'],
      learningPoint: 'Overall health arguments often combine scientific explanation with practical implications - here: essential process with serious consequences but strategies for improvement'
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

