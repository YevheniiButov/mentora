// Reading Comprehension Lesson 001: Artificial Intelligence in Healthcare
// Learning-Oriented Format with Progressive Difficulty

export const lesson001 = {
  id: 'lesson_001',
  title: 'Artificial Intelligence in Healthcare',
  language: 'English',
  professionContext: 'Medical professionals reading scientific content',
  estimatedTime: 15, // minutes
  imageUrl: '/static/images/passages/ai-healthcare.png',
  
  text: `A Artificial intelligence is rapidly transforming the healthcare industry, offering unprecedented opportunities to improve patient outcomes and streamline medical processes. Machine learning algorithms can now analyze vast amounts of medical data with remarkable speed and accuracy, identifying patterns that might escape human observation. Recent studies have shown that AI systems can diagnose certain conditions, such as skin cancer and diabetic retinopathy, with accuracy rates comparable to or exceeding those of experienced physicians. This technological advancement has sparked intense debate about the future role of human doctors in an increasingly automated medical landscape.

B The implementation of AI in clinical settings extends far beyond diagnostic applications. Predictive analytics powered by artificial intelligence can forecast patient deterioration hours before traditional warning signs appear, allowing medical staff to intervene proactively. In drug discovery, AI algorithms can screen millions of molecular compounds in days rather than years, accelerating the development of new treatments. Furthermore, AI-driven robotic systems are assisting surgeons in performing complex procedures with enhanced precision, reducing operation times and improving recovery rates. However, these innovations come with significant challenges, including the need for massive datasets to train algorithms effectively and concerns about data privacy and security.

C Despite the promising applications, the integration of AI into healthcare faces substantial obstacles. Many healthcare professionals express concern about over-reliance on automated systems, arguing that medicine requires human empathy and judgment that machines cannot replicate. There are also questions about liability when AI systems make errors, and regulatory frameworks have struggled to keep pace with technological advancement. Additionally, the substantial initial investment required for AI implementation presents a barrier for smaller medical facilities, potentially widening the gap between well-funded institutions and those serving underserved communities. Nevertheless, experts predict that within the next decade, AI will become an indispensable tool in modern medicine, fundamentally changing how healthcare is delivered worldwide.`,

  paragraphs: [
    {
      id: 'para_a',
      label: 'A',
      content: 'Artificial intelligence is rapidly transforming the healthcare industry, offering unprecedented opportunities to improve patient outcomes and streamline medical processes. Machine learning algorithms can now analyze vast amounts of medical data with remarkable speed and accuracy, identifying patterns that might escape human observation. Recent studies have shown that AI systems can diagnose certain conditions, such as skin cancer and diabetic retinopathy, with accuracy rates comparable to or exceeding those of experienced physicians. This technological advancement has sparked intense debate about the future role of human doctors in an increasingly automated medical landscape.',
      mainTopic: 'AI diagnostic capabilities and their impact on healthcare',
      keyDates: []
    },
    {
      id: 'para_b',
      label: 'B',
      content: 'The implementation of AI in clinical settings extends far beyond diagnostic applications. Predictive analytics powered by artificial intelligence can forecast patient deterioration hours before traditional warning signs appear, allowing medical staff to intervene proactively. In drug discovery, AI algorithms can screen millions of molecular compounds in days rather than years, accelerating the development of new treatments. Furthermore, AI-driven robotic systems are assisting surgeons in performing complex procedures with enhanced precision, reducing operation times and improving recovery rates. However, these innovations come with significant challenges, including the need for massive datasets to train algorithms effectively and concerns about data privacy and security.',
      mainTopic: 'Broader AI applications in clinical settings and associated challenges',
      keyDates: []
    },
    {
      id: 'para_c',
      label: 'C',
      content: 'Despite the promising applications, the integration of AI into healthcare faces substantial obstacles. Many healthcare professionals express concern about over-reliance on automated systems, arguing that medicine requires human empathy and judgment that machines cannot replicate. There are also questions about liability when AI systems make errors, and regulatory frameworks have struggled to keep pace with technological advancement. Additionally, the substantial initial investment required for AI implementation presents a barrier for smaller medical facilities, potentially widening the gap between well-funded institutions and those serving underserved communities. Nevertheless, experts predict that within the next decade, AI will become an indispensable tool in modern medicine, fundamentally changing how healthcare is delivered worldwide.',
      mainTopic: 'Obstacles to AI integration and future predictions',
      keyDates: []
    }
  ],

  vocabulary: [
    {
      id: 'vocab_1',
      word: 'unprecedented',
      partOfSpeech: 'adjective',
      definition: 'never done or known before',
      contextSentence: 'offering unprecedented opportunities to improve patient outcomes',
      explanationInContext: 'AI is providing opportunities that have never existed before in healthcare history',
      synonyms: ['unparalleled', 'novel', 'groundbreaking'],
      usage: 'Used to describe something that is completely new or has no previous example',
      medicalConnection: null
    },
    {
      id: 'vocab_2',
      word: 'streamline',
      partOfSpeech: 'verb',
      definition: 'to make more efficient or simpler',
      contextSentence: 'streamline medical processes',
      explanationInContext: 'AI helps make medical procedures faster and more efficient',
      synonyms: ['simplify', 'optimize', 'improve efficiency'],
      usage: 'Commonly used in business and technology contexts to describe process improvement',
      medicalConnection: null
    },
    {
      id: 'vocab_3',
      word: 'remarkable',
      partOfSpeech: 'adjective',
      definition: 'worthy of attention; extraordinary',
      contextSentence: 'with remarkable speed and accuracy',
      explanationInContext: 'The speed and accuracy of AI are exceptional and noteworthy',
      synonyms: ['extraordinary', 'notable', 'impressive'],
      usage: 'Used to emphasize something that stands out or is unusually good',
      medicalConnection: null
    },
    {
      id: 'vocab_4',
      word: 'retinopathy',
      partOfSpeech: 'noun',
      definition: 'disease of the retina',
      contextSentence: 'diabetic retinopathy',
      explanationInContext: 'A specific eye condition related to diabetes that AI can help diagnose',
      synonyms: ['retinal disease'],
      usage: 'Medical term for retinal disorders',
      medicalConnection: 'Direct medical term - condition affecting the retina, often related to diabetes'
    },
    {
      id: 'vocab_5',
      word: 'proactively',
      partOfSpeech: 'adverb',
      definition: 'taking action in advance rather than reacting',
      contextSentence: 'allowing medical staff to intervene proactively',
      explanationInContext: 'Doctors can act before problems become serious, rather than waiting to react',
      synonyms: ['preventively', 'in advance', 'preemptively'],
      usage: 'Used when describing actions taken to prevent problems before they occur',
      medicalConnection: 'Important concept in preventive medicine and early intervention'
    },
    {
      id: 'vocab_6',
      word: 'molecular',
      partOfSpeech: 'adjective',
      definition: 'relating to molecules, the smallest units of a substance',
      contextSentence: 'screen millions of molecular compounds',
      explanationInContext: 'AI analyzes tiny chemical structures to find potential drugs',
      synonyms: ['chemical', 'atomic'],
      usage: 'Scientific term used in chemistry, biology, and pharmacology',
      medicalConnection: 'Essential in drug development and pharmaceutical research'
    },
    {
      id: 'vocab_7',
      word: 'precision',
      partOfSpeech: 'noun',
      definition: 'the quality of being exact and accurate',
      contextSentence: 'performing complex procedures with enhanced precision',
      explanationInContext: 'Robots can perform surgeries with very exact movements',
      synonyms: ['accuracy', 'exactness', 'preciseness'],
      usage: 'Used when describing exactness in technical or scientific contexts',
      medicalConnection: 'Critical in surgical procedures and medical measurements'
    },
    {
      id: 'vocab_8',
      word: 'replicate',
      partOfSpeech: 'verb',
      definition: 'to copy or reproduce',
      contextSentence: 'human empathy and judgment that machines cannot replicate',
      explanationInContext: 'Machines cannot copy or reproduce human emotional understanding',
      synonyms: ['copy', 'duplicate', 'reproduce', 'imitate'],
      usage: 'Used when something cannot be exactly copied or matched',
      medicalConnection: null
    },
    {
      id: 'vocab_9',
      word: 'liability',
      partOfSpeech: 'noun',
      definition: 'legal responsibility for something',
      contextSentence: 'questions about liability when AI systems make errors',
      explanationInContext: 'Who is legally responsible when AI makes mistakes in medical decisions',
      synonyms: ['responsibility', 'accountability', 'legal responsibility'],
      usage: 'Legal term used when discussing who is responsible for errors or damages',
      medicalConnection: 'Important in medical malpractice and healthcare law'
    },
    {
      id: 'vocab_10',
      word: 'indispensable',
      partOfSpeech: 'adjective',
      definition: 'absolutely necessary; essential',
      contextSentence: 'AI will become an indispensable tool in modern medicine',
      explanationInContext: 'AI will become so essential that medicine cannot function without it',
      synonyms: ['essential', 'crucial', 'vital', 'necessary'],
      usage: 'Used to describe something that is absolutely required',
      medicalConnection: null
    }
  ],

  questions: [
    // ========== LEVEL 1: VOCABULARY IN CONTEXT (2 questions) ==========
    {
      id: 'q1',
      level: 1,
      type: 'vocabulary_context',
      difficulty: 'easy',
      paragraph: 'para_a',
      question: 'What does "unprecedented" mean in the context of AI in healthcare?',
      text: 'offering unprecedented opportunities to improve patient outcomes',
      options: [
        {
          id: 'q1_a',
          text: 'Never done or known before',
          correct: true,
          explanation: 'Correct. "Unprecedented" means something that has never happened, been done, or been known before. In this context, AI is providing diagnostic opportunities and capabilities that have never existed in healthcare history, representing a completely new development without any previous example or precedent.'
        },
        {
          id: 'q1_b',
          text: 'Very expensive and costly to implement',
          correct: false,
          explanation: 'While AI implementation can be expensive, "unprecedented" doesn\'t refer to cost, expense, or financial aspects. It means something completely new, novel, or without previous example. The word describes novelty and lack of precedent, not economic factors or implementation costs.'
        },
        {
          id: 'q1_c',
          text: 'Well-documented and thoroughly researched',
          correct: false,
          explanation: 'This is the opposite meaning. "Unprecedented" means something has no previous example, documentation, or precedent - it\'s completely new and has never occurred before. If something is unprecedented, it cannot be well-documented because there is no previous occurrence to document.'
        },
        {
          id: 'q1_d',
          text: 'Similar to previous methods and approaches',
          correct: false,
          explanation: 'This contradicts the meaning. "Unprecedented" specifically means unlike anything that came before, completely new, and without any previous example or similarity. If something is unprecedented, it cannot be similar to previous methods because it represents something that has never existed before.'
        }
      ],
      hint: 'Think about what word describes something that has never happened before in history.',
      relatedVocabulary: ['vocab_1'],
      learningPoint: 'Context clues help determine meaning - "unprecedented opportunities" suggests something completely new'
    },
    {
      id: 'q2',
      level: 1,
      type: 'vocabulary_context',
      difficulty: 'easy',
      paragraph: 'para_b',
      question: 'What does "proactively" mean when describing medical intervention?',
      text: 'allowing medical staff to intervene proactively',
      options: [
        {
          id: 'q2_a',
          text: 'Taking action in advance before problems become serious',
          correct: true,
          explanation: 'Correct. "Proactively" means acting in advance to prevent problems, rather than waiting to react after something goes wrong. In medicine, this means treating issues and intervening before they become critical, which is a key advantage of AI systems that can predict patient deterioration hours before traditional warning signs appear.'
        },
        {
          id: 'q2_b',
          text: 'Reacting quickly after a problem occurs or develops',
          correct: false,
          explanation: 'This describes reactive behavior, not proactive. "Proactively" means acting before problems happen or develop, not after they occur. The text specifically mentions intervening "hours before traditional warning signs appear," emphasizing the advance nature of proactive action.'
        },
        {
          id: 'q2_c',
          text: 'Using advanced technology and modern equipment',
          correct: false,
          explanation: 'While AI is advanced technology, "proactively" refers to the timing of action (before problems occur), not the type of technology or equipment used. The word describes when action is taken, not how technologically advanced the tools are.'
        },
        {
          id: 'q2_d',
          text: 'Following standard procedures and established protocols',
          correct: false,
          explanation: '"Proactively" is about when action is taken (in advance, before problems develop), not about following procedures or protocols. It emphasizes prevention and early intervention over reactive responses, regardless of which procedures are used.'
        }
      ],
      hint: 'The text mentions "hours before traditional warning signs appear" - what does this tell you about when action is taken?',
      relatedVocabulary: ['vocab_5'],
      learningPoint: 'Understanding "proactive" vs "reactive" is crucial in medical contexts - prevention is often better than treatment'
    },
    // ========== LEVEL 2: MAIN IDEA IDENTIFICATION (2 questions) ==========
    {
      id: 'q3',
      level: 2,
      type: 'main_idea',
      difficulty: 'medium',
      paragraph: 'para_a',
      question: 'What is the main idea of paragraph A?',
      text: 'Paragraph A discusses AI diagnostic capabilities...',
      options: [
        {
          id: 'q3_a',
          text: 'AI can diagnose skin cancer better than human doctors',
          correct: false,
          explanation: 'This is a specific detail mentioned as an example to illustrate AI\'s capabilities, not the main idea of the paragraph. The paragraph discusses AI\'s broader diagnostic capabilities across multiple areas and the debate they\'ve sparked about the future of medicine, not just one specific application.'
        },
        {
          id: 'q3_b',
          text: 'AI is transforming healthcare with diagnostic capabilities matching or exceeding physicians',
          correct: true,
          explanation: 'This captures the main idea: (1) AI is transforming healthcare as a field, (2) it has remarkable diagnostic capabilities that can analyze medical data, (3) it can match or exceed physicians in accuracy (as shown in examples like skin cancer and diabetic retinopathy diagnosis), and (4) this has sparked intense debate about doctors\' future role. The paragraph presents AI as a transformative force while acknowledging the controversy it creates.'
        },
        {
          id: 'q3_c',
          text: 'Machine learning algorithms process information very quickly and efficiently',
          correct: false,
          explanation: 'This is a supporting detail about how AI works technically, not the main idea. While speed and efficiency might be mentioned, the paragraph is primarily about AI\'s diagnostic capabilities and the debate about its role in healthcare, not about the technical speed of algorithms. The main idea focuses on transformation and capabilities, not processing speed.'
        },
        {
          id: 'q3_d',
          text: 'Doctors will be completely replaced by advanced AI technology systems',
          correct: false,
          explanation: 'The paragraph mentions "intense debate" about the future role of doctors, but doesn\'t conclude they will be replaced. It presents the debate and controversy, not a definitive conclusion. The text discusses capabilities and sparks discussion about the future, but doesn\'t make predictions about replacement. The focus is on transformation and debate, not replacement.'
        }
      ],
      hint: 'A main idea should cover the whole paragraph. Ask yourself: "What is the author\'s main point about AI in healthcare in this paragraph?"',
      relatedVocabulary: ['vocab_1', 'vocab_2', 'vocab_3'],
      learningPoint: 'Main ideas are broader than details - they encompass the entire paragraph\'s purpose, not just one example or fact'
    },
    {
      id: 'q4',
      level: 2,
      type: 'main_idea',
      difficulty: 'medium',
      paragraph: 'para_c',
      question: 'What is the central theme of paragraph C?',
      options: [
        {
          id: 'q4_a',
          text: 'AI will completely replace human doctors in healthcare',
          correct: false,
          explanation: 'The paragraph discusses obstacles, concerns, and challenges to AI integration, not replacement. It mentions AI becoming "indispensable" (meaning essential as a tool), but doesn\'t suggest complete replacement of human doctors. The focus is on integration challenges, not replacement.'
        },
        {
          id: 'q4_b',
          text: 'AI integration faces obstacles but experts predict it will become essential',
          correct: true,
          explanation: 'This captures the paragraph\'s structure: it presents multiple obstacles (professional concerns about over-reliance, liability questions when errors occur, regulatory frameworks struggling to keep pace, cost barriers creating inequality between well-funded and smaller institutions) but concludes with expert prediction that AI will become indispensable despite these challenges. The paragraph balances realistic obstacles with optimistic future outlook.'
        },
        {
          id: 'q4_c',
          text: 'Smaller medical facilities cannot afford expensive AI technology and systems',
          correct: false,
          explanation: 'This is one specific obstacle mentioned (cost barriers creating inequality between institutions), but it\'s not the main theme of the paragraph. The paragraph discusses multiple obstacles including professional concerns about over-reliance, liability issues when errors occur, regulatory frameworks struggling to keep pace, and cost barriers, then ends with a prediction about AI becoming essential despite these challenges.'
        },
        {
          id: 'q4_d',
          text: 'Regulatory frameworks have successfully adapted to rapid AI development and innovation',
          correct: false,
          explanation: 'The text states the opposite - regulatory frameworks "have struggled to keep pace" with rapid AI advancement, which is presented as an obstacle and challenge, not a success. This is one of several obstacles discussed in the paragraph, along with professional concerns, liability issues, and cost barriers.'
        }
      ],
      hint: 'The paragraph discusses challenges but ends with a prediction. What is the overall message about obstacles and future?',
      relatedVocabulary: ['vocab_8', 'vocab_9', 'vocab_10'],
      learningPoint: 'Main ideas often balance challenges with future outlook - recognizing both obstacles and predictions helps understand the author\'s perspective'
    },
    // ========== LEVEL 3: INFERENCE & ANALYSIS (2 questions) ==========
    {
      id: 'q5',
      level: 3,
      type: 'inference',
      difficulty: 'hard',
      paragraph: 'para_b',
      question: 'Why does the author mention that AI can screen compounds "in days rather than years"?',
      options: [
        {
          id: 'q5_a',
          text: 'To emphasize AI\'s speed advantage over traditional methods',
          correct: true,
          explanation: 'Correct. The dramatic time difference (days vs years) highlights one of AI\'s major advantages - speed. This comparison emphasizes how AI can accelerate drug discovery by screening millions of molecular compounds in days rather than years, which is crucial for developing new treatments faster and more efficiently. The author uses this specific comparison to demonstrate AI\'s transformative potential in pharmaceutical research.'
        },
        {
          id: 'q5_b',
          text: 'To criticize traditional drug discovery methods as outdated',
          correct: false,
          explanation: 'The author isn\'t criticizing - they\'re highlighting AI\'s capability and advancement. The comparison shows improvement and progress, not criticism of the old methods. The focus is on AI\'s benefits and transformative potential, not problems with traditional approaches. The tone is positive about AI, not negative about existing methods.'
        },
        {
          id: 'q5_c',
          text: 'To suggest AI reduces financial costs of drug discovery',
          correct: false,
          explanation: 'While faster processes might eventually reduce costs, the text specifically emphasizes time ("days rather than years"), not cost or financial implications. The focus is explicitly on speed and efficiency of screening compounds, not economic benefits. The comparison is about time savings, not money savings.'
        },
        {
          id: 'q5_d',
          text: 'To explain how molecular compounds work and function',
          correct: false,
          explanation: 'The sentence is about the speed and efficiency of screening compounds using AI, not explaining how compounds themselves work or function. The focus is on the process of discovery and the time it takes, not the scientific properties or mechanisms of compounds. The text discusses AI\'s screening capability, not compound chemistry.'
        }
      ],
      hint: 'What does the dramatic time difference (days vs years) tell you about why the author included this detail?',
      relatedVocabulary: ['vocab_6'],
      learningPoint: 'Authors use specific time comparisons to emphasize advantages - dramatic differences highlight key benefits'
    },
    {
      id: 'q6',
      level: 3,
      type: 'inference',
      difficulty: 'hard',
      paragraph: 'para_c',
      question: 'What does the author suggest by mentioning that AI investment "potentially widening the gap between well-funded institutions and those serving underserved communities"?',
      options: [
        {
          id: 'q6_a',
          text: 'AI will make healthcare access more equal for everyone',
          correct: false,
          explanation: 'This contradicts the statement. The text explicitly says it "widens the gap," meaning it increases inequality rather than reducing it. The author is expressing concern about growing disparities, not suggesting equality. The phrase "widening the gap" directly indicates increasing inequality.'
        },
        {
          id: 'q6_b',
          text: 'AI adoption may increase inequality between well-funded and smaller institutions',
          correct: true,
          explanation: 'Correct. The phrase "widening the gap" suggests that AI could make healthcare disparities worse. Well-funded institutions can afford the substantial initial investment required for AI implementation, but smaller facilities serving underserved communities cannot, potentially creating a two-tier healthcare system where only wealthier institutions benefit from advanced technology. This raises concerns about equitable access to cutting-edge medical tools.'
        },
        {
          id: 'q6_c',
          text: 'All medical facilities will eventually have equal access to AI technology',
          correct: false,
          explanation: 'The text suggests the opposite - that the gap is actively widening, not that equality will be achieved. The concern is about ongoing and increasing disparities between institutions, not eventual parity. The author presents this as a current problem, not a future solution.'
        },
        {
          id: 'q6_d',
          text: 'Underserved communities do not need advanced medical technology',
          correct: false,
          explanation: 'The author isn\'t suggesting this. The concern is that these communities won\'t have access to technology they need and deserve, not that they don\'t need it. The issue is access, affordability, and equity - the author recognizes these communities need the technology but cannot access it.'
        }
      ],
      hint: 'Think about what "widening the gap" means. What happens when some institutions can afford new technology and others cannot?',
      relatedVocabulary: ['vocab_10'],
      learningPoint: 'Inference questions require understanding implications - "widening the gap" suggests increasing inequality, not just a neutral fact'
    },
    // ========== LEVEL 4: SYNTHESIS & COMPARISON (2 questions) ==========
    {
      id: 'q7',
      level: 4,
      type: 'synthesis',
      difficulty: 'very_hard',
      paragraph: null,
      question: 'How does the author develop the argument about AI\'s role in healthcare across all three paragraphs?',
      text: 'The text progresses from capabilities to applications to obstacles...',
      options: [
        {
          id: 'q7_a',
          text: 'From diagnostic capabilities to clinical applications to obstacles and future predictions',
          correct: true,
          explanation: 'Perfect synthesis. Paragraph A establishes AI\'s diagnostic capabilities (analyzing medical data, diagnosing conditions like skin cancer and diabetic retinopathy) and the debate they spark about doctors\' future role. Paragraph B expands to broader clinical applications (predictive analytics forecasting patient deterioration, drug discovery screening compounds, AI-driven robotic surgery) while acknowledging challenges like data needs and privacy concerns. Paragraph C presents obstacles (professional concerns about over-reliance, liability questions, regulatory struggles, cost barriers creating inequality) but concludes with expert prediction that AI will become indispensable. This shows a logical progression from "what AI can do" to "how it\'s used" to "what stands in the way but why it will succeed anyway," balancing promise with realism.'
        },
        {
          id: 'q7_b',
          text: 'From problems to solutions to additional problems and challenges',
          correct: false,
          explanation: 'This oversimplifies and mischaracterizes the text. The text doesn\'t present AI as a problem - it presents it as transformative technology with remarkable capabilities. While obstacles are discussed, they\'re framed as challenges to overcome, not as problems that define AI. The overall narrative is positive about AI\'s potential despite recognizing hurdles. The structure is about progressive development, not problem cycles.'
        },
        {
          id: 'q7_c',
          text: 'From past achievements to current applications to future development plans',
          correct: false,
          explanation: 'The text doesn\'t discuss past achievements or historical development of AI. Instead, it focuses on current capabilities (what AI can do now) and future integration predictions (what experts say will happen). The timeline is about present state and future outlook, not historical progression from past to present to future.'
        },
        {
          id: 'q7_d',
          text: 'From general information to specific examples to final summary conclusions',
          correct: false,
          explanation: 'While there\'s some structural truth to this pattern, it misses the key thematic progression: capabilities → applications → obstacles. The conclusion isn\'t just a summary of information - it\'s a forward-looking prediction about AI becoming indispensable despite the obstacles discussed. The structure is more about functional progression (what it does, how it\'s used, what challenges exist) than informational hierarchy from general to specific.'
        }
      ],
      hint: 'Look at how each paragraph builds on the previous one. What does A establish? What does B add? How does C address challenges while maintaining the overall positive outlook?',
      relatedVocabulary: ['vocab_1', 'vocab_5', 'vocab_8', 'vocab_10'],
      learningPoint: 'Synthesis requires seeing the overall argument structure - here: capabilities → applications → obstacles → future prediction. The author balances promise with realism.'
    },
    {
      id: 'q8',
      level: 4,
      type: 'synthesis',
      difficulty: 'very_hard',
      paragraph: null,
      question: 'Based on the entire text, what is the author\'s overall perspective on AI in healthcare?',
      options: [
        {
          id: 'q8_a',
          text: 'AI is promising but faces obstacles; experts predict it will become essential',
          correct: true,
          explanation: 'This captures the balanced perspective: The author acknowledges AI\'s remarkable capabilities (diagnosing conditions with accuracy matching or exceeding physicians, predicting patient deterioration hours early, screening millions of compounds in days, assisting surgeons with precision), recognizes substantial obstacles (professional concerns about over-reliance and loss of human judgment, liability questions when errors occur, regulatory frameworks struggling to keep pace, cost barriers creating inequality between institutions), but concludes with expert prediction that AI will become indispensable within the next decade. This shows a realistic but ultimately optimistic view that acknowledges challenges while maintaining confidence in AI\'s transformative potential.'
        },
        {
          id: 'q8_b',
          text: 'AI will completely replace human doctors within the next decade',
          correct: false,
          explanation: 'The text mentions "intense debate" about doctors\' future role but doesn\'t conclude replacement. It says AI will become "indispensable" (meaning an essential tool that doctors use), not that it will replace humans. The discussion focuses on AI as a transformative tool that changes how healthcare is delivered, not as a replacement for human medical professionals and their empathy and judgment.'
        },
        {
          id: 'q8_c',
          text: 'AI is too expensive and problematic to be useful in healthcare settings',
          correct: false,
          explanation: 'While obstacles including cost are mentioned, the text emphasizes AI\'s remarkable capabilities throughout and ends with expert prediction that it will become essential. The overall tone balances realism about challenges with strong optimism about AI\'s future. Cost is presented as a barrier for some institutions, not as a reason AI is unusable. The text celebrates AI\'s potential despite recognizing hurdles.'
        },
        {
          id: 'q8_d',
          text: 'AI only works effectively for diagnosing specific skin conditions',
          correct: false,
          explanation: 'This is far too narrow and inaccurate. The text describes AI\'s use across multiple areas: diagnostics (skin cancer, diabetic retinopathy, and other conditions), predictive analytics (forecasting patient deterioration), drug discovery (screening molecular compounds), robotic surgery assistance, and more. Skin cancer diagnosis is presented as one example among many capabilities, not the only use.'
        }
      ],
      hint: 'Consider how the author balances the positive aspects (capabilities, applications) with obstacles (concerns, challenges) and ends with a prediction. What does this balance suggest?',
      relatedVocabulary: ['vocab_1', 'vocab_2', 'vocab_5', 'vocab_8', 'vocab_10'],
      learningPoint: 'Overall perspective synthesis: Look for how authors balance positive and negative aspects, then see where they land. Here: realistic about challenges but optimistic about future integration.'
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

