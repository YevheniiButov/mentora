// Reading Comprehension Lesson 007: The Evolution of Human Language
export const lesson007 = {
  id: 'lesson_007',
  title: 'The Evolution of Human Language',
  language: 'English',
  professionContext: 'Medical professionals reading scientific content',
  estimatedTime: 15,
  imageUrl: '/static/images/passages/language-evolution.png',
  
  text: `A The origin of human language remains one of the most intriguing mysteries in evolutionary science, with scholars debating when, how, and why our species developed this unique communication system. Unlike animal communication, which typically conveys immediate information about threats, food sources, or mating opportunities, human language possesses several distinctive features: it is symbolic (words represent concepts rather than directly signaling things), generative (finite rules allow infinite sentence creation), and can describe abstract concepts, past events, and hypothetical scenarios. These characteristics enable humans to share complex ideas, transmit cultural knowledge across generations, and engage in collaborative planning—capabilities that arguably underpin human civilization's development. However, language leaves no fossil record, making its evolutionary trajectory difficult to trace definitively.

B Researchers have proposed various theories about language evolution's timeline and mechanisms. Some scholars advocate for a relatively recent and rapid emergence, suggesting language appeared between 50,000 and 100,000 years ago in anatomically modern humans, possibly coinciding with a genetic mutation that reorganized brain structures. This "sudden emergence" theory finds support in the archaeological record's apparent behavioral revolution around 50,000 years ago, marked by sophisticated tools, art, and long-distance trade networks that might indicate advanced linguistic capabilities. Alternative theories propose a more gradual evolution, with proto-linguistic systems emerging much earlier in human ancestors, perhaps 2 million years ago with Homo habilis, and gradually increasing in complexity. Comparative studies of primate communication reveal that great apes possess some precursor abilities—they can learn symbolic associations and combine symbols in simple ways—suggesting language evolution built upon existing cognitive capacities rather than appearing completely de novo.

C Neurological and genetic research provides additional insights into language evolution. The FOXP2 gene, sometimes called the "language gene," appears crucial for the fine motor control required for speech production. Humans possess a variant of this gene that differs from the versions found in other primates, and this variant emerged approximately 200,000 years ago. Individuals with FOXP2 mutations experience severe speech and language difficulties, demonstrating its importance. Brain imaging studies reveal that language processing activates specific regions, particularly Broca's area (speech production) and Wernicke's area (language comprehension) in the left hemisphere. These specialized brain regions suggest language has been subject to strong evolutionary selection pressures. Some researchers propose that language evolution was driven by social needs—managing increasingly complex group relationships required more sophisticated communication. Others emphasize practical advantages for coordinating hunting, sharing resources, and transmitting survival knowledge. Regardless of the specific pressures, language evolution clearly provided such enormous advantages that it became a defining human characteristic, fundamentally shaping how our species understands and interacts with the world.`,

  paragraphs: [
    {
      id: 'para_a',
      label: 'A',
      content: 'The origin of human language remains one of the most intriguing mysteries in evolutionary science, with scholars debating when, how, and why our species developed this unique communication system. Unlike animal communication, which typically conveys immediate information about threats, food sources, or mating opportunities, human language possesses several distinctive features: it is symbolic (words represent concepts rather than directly signaling things), generative (finite rules allow infinite sentence creation), and can describe abstract concepts, past events, and hypothetical scenarios. These characteristics enable humans to share complex ideas, transmit cultural knowledge across generations, and engage in collaborative planning—capabilities that arguably underpin human civilization\'s development. However, language leaves no fossil record, making its evolutionary trajectory difficult to trace definitively.',
      mainTopic: 'Human language as a unique communication system with distinctive features and its role in civilization, but difficulty in tracing its evolution',
      keyDates: []
    },
    {
      id: 'para_b',
      label: 'B',
      content: 'Researchers have proposed various theories about language evolution\'s timeline and mechanisms. Some scholars advocate for a relatively recent and rapid emergence, suggesting language appeared between 50,000 and 100,000 years ago in anatomically modern humans, possibly coinciding with a genetic mutation that reorganized brain structures. This "sudden emergence" theory finds support in the archaeological record\'s apparent behavioral revolution around 50,000 years ago, marked by sophisticated tools, art, and long-distance trade networks that might indicate advanced linguistic capabilities. Alternative theories propose a more gradual evolution, with proto-linguistic systems emerging much earlier in human ancestors, perhaps 2 million years ago with Homo habilis, and gradually increasing in complexity. Comparative studies of primate communication reveal that great apes possess some precursor abilities—they can learn symbolic associations and combine symbols in simple ways—suggesting language evolution built upon existing cognitive capacities rather than appearing completely de novo.',
      mainTopic: 'Competing theories about when language evolved (sudden vs. gradual) and evidence from archaeology and primate studies',
      keyDates: ['50,000-100,000 years ago', '2 million years ago']
    },
    {
      id: 'para_c',
      label: 'C',
      content: 'Neurological and genetic research provides additional insights into language evolution. The FOXP2 gene, sometimes called the "language gene," appears crucial for the fine motor control required for speech production. Humans possess a variant of this gene that differs from the versions found in other primates, and this variant emerged approximately 200,000 years ago. Individuals with FOXP2 mutations experience severe speech and language difficulties, demonstrating its importance. Brain imaging studies reveal that language processing activates specific regions, particularly Broca\'s area (speech production) and Wernicke\'s area (language comprehension) in the left hemisphere. These specialized brain regions suggest language has been subject to strong evolutionary selection pressures. Some researchers propose that language evolution was driven by social needs—managing increasingly complex group relationships required more sophisticated communication. Others emphasize practical advantages for coordinating hunting, sharing resources, and transmitting survival knowledge. Regardless of the specific pressures, language evolution clearly provided such enormous advantages that it became a defining human characteristic, fundamentally shaping how our species understands and interacts with the world.',
      mainTopic: 'Genetic and neurological evidence for language evolution, and theories about why language evolved (social vs. practical advantages)',
      keyDates: ['200,000 years ago']
    }
  ],

  vocabulary: [
    {
      id: 'vocab_1',
      word: 'intriguing',
      partOfSpeech: 'adjective',
      definition: 'very interesting or fascinating',
      contextSentence: 'one of the most intriguing mysteries',
      explanationInContext: 'The origin of language is a very fascinating and interesting mystery that scientists are still trying to solve',
      synonyms: ['fascinating', 'interesting', 'captivating'],
      usage: 'Used to describe something that captures attention and interest',
      medicalConnection: null
    },
    {
      id: 'vocab_2',
      word: 'symbolic',
      partOfSpeech: 'adjective',
      definition: 'representing something else rather than being the thing itself',
      contextSentence: 'it is symbolic (words represent concepts rather than directly signaling things)',
      explanationInContext: 'Words are symbols - they represent ideas, not the actual things. For example, the word "tree" represents the concept of a tree, not an actual tree.',
      synonyms: ['representative', 'metaphorical'],
      usage: 'Used when something stands for or represents something else',
      medicalConnection: null
    },
    {
      id: 'vocab_3',
      word: 'generative',
      partOfSpeech: 'adjective',
      definition: 'able to produce or create new things',
      contextSentence: 'generative (finite rules allow infinite sentence creation)',
      explanationInContext: 'Language can create unlimited new sentences from a limited set of rules - we can always make new sentences we\'ve never heard before',
      synonyms: ['productive', 'creative', 'prolific'],
      usage: 'Used to describe systems that can produce unlimited new outputs from limited rules',
      medicalConnection: null
    },
    {
      id: 'vocab_4',
      word: 'underpin',
      partOfSpeech: 'verb',
      definition: 'to support or form the foundation of',
      contextSentence: 'capabilities that arguably underpin human civilization\'s development',
      explanationInContext: 'Language supports and is the foundation for human civilization - without language, civilization couldn\'t have developed',
      synonyms: ['support', 'found', 'base', 'underlie'],
      usage: 'Used when something provides essential support or foundation',
      medicalConnection: null
    },
    {
      id: 'vocab_5',
      word: 'trajectory',
      partOfSpeech: 'noun',
      definition: 'the path or course of development',
      contextSentence: 'making its evolutionary trajectory difficult to trace',
      explanationInContext: 'The path or course of how language evolved over time is hard to follow because there\'s no fossil record',
      synonyms: ['path', 'course', 'development', 'evolution'],
      usage: 'Used to describe the path or course something takes over time',
      medicalConnection: null
    },
    {
      id: 'vocab_6',
      word: 'advocate',
      partOfSpeech: 'verb',
      definition: 'to publicly support or recommend',
      contextSentence: 'Some scholars advocate for a relatively recent and rapid emergence',
      explanationInContext: 'Some researchers support and argue for the idea that language appeared recently and quickly',
      synonyms: ['support', 'argue for', 'promote', 'champion'],
      usage: 'Used when someone publicly supports a particular idea or position',
      medicalConnection: null
    },
    {
      id: 'vocab_7',
      word: 'precursor',
      partOfSpeech: 'noun',
      definition: 'something that comes before and leads to something else',
      contextSentence: 'great apes possess some precursor abilities',
      explanationInContext: 'Apes have some abilities that came before full language - these are early versions or foundations of language abilities',
      synonyms: ['forerunner', 'antecedent', 'predecessor'],
      usage: 'Used to describe something that comes before and is a foundation for something else',
      medicalConnection: 'Medical term - precursor cells, precursor molecules in biochemistry'
    },
    {
      id: 'vocab_8',
      word: 'de novo',
      partOfSpeech: 'phrase',
      definition: 'from the beginning; completely new',
      contextSentence: 'rather than appearing completely de novo',
      explanationInContext: 'Language didn\'t appear completely new from nothing - it built on existing abilities that apes already had',
      synonyms: ['from scratch', 'anew', 'from the beginning'],
      usage: 'Latin phrase used in scientific contexts to mean "from the beginning" or "completely new"',
      medicalConnection: 'Common in medical/scientific terminology - "de novo mutation" means a new mutation not inherited'
    },
    {
      id: 'vocab_9',
      word: 'variant',
      partOfSpeech: 'noun',
      definition: 'a different version or form of something',
      contextSentence: 'Humans possess a variant of this gene',
      explanationInContext: 'Humans have a different version of the FOXP2 gene compared to other primates - it\'s been modified',
      synonyms: ['version', 'form', 'type', 'strain'],
      usage: 'Used to describe different versions of the same thing',
      medicalConnection: 'Common in genetics and medicine - genetic variants, virus variants'
    },
    {
      id: 'vocab_10',
      word: 'selection pressures',
      partOfSpeech: 'noun',
      definition: 'environmental forces that favor certain traits in evolution',
      contextSentence: 'language has been subject to strong evolutionary selection pressures',
      explanationInContext: 'Evolution favored language abilities because they provided advantages - people with better language skills survived and reproduced better',
      synonyms: ['evolutionary forces', 'selective forces'],
      usage: 'Scientific term for forces in evolution that favor certain traits',
      medicalConnection: 'Important in understanding disease evolution and antibiotic resistance'
    }
  ],

  questions: [
    {
      id: 'q1',
      level: 1,
      type: 'vocabulary_context',
      difficulty: 'easy',
      paragraph: 'para_a',
      question: 'What does "generative" mean when describing human language?',
      text: 'generative (finite rules allow infinite sentence creation)',
      options: [
        {
          id: 'q1_a',
          text: 'Able to create unlimited new sentences from a limited set of rules',
          correct: true,
          explanation: 'Correct. "Generative" means language can produce unlimited new sentences from finite components. We have a finite set of grammar rules and vocabulary, but we can combine words in infinite ways to create sentences we\'ve never heard before. This creative capacity is what makes human language generative and distinguishes it from simple communication systems.'
        },
        {
          id: 'q1_b',
          text: 'Only able to repeat existing sentences and phrases',
          correct: false,
          explanation: 'This is the opposite meaning. "Generative" means language can create new, original sentences, not just repeat old ones. The text explicitly says "infinite sentence creation" and "finite rules allow infinite sentence creation," emphasizing the creative, productive capacity of language.'
        },
        {
          id: 'q1_c',
          text: 'Very loud and clear in sound and pronunciation',
          correct: false,
          explanation: '"Generative" refers to the ability to create and produce new things (sentences), not to volume, clarity, or sound quality. It\'s about productivity and creativity in language, not acoustic properties or how clearly something is spoken.'
        },
        {
          id: 'q1_d',
          text: 'Easy to learn and master quickly',
          correct: false,
          explanation: '"Generative" describes language\'s ability to create unlimited new sentences from finite rules, not how easy or difficult it is to learn. It\'s about the productive capacity and creative potential of language, not the learning process or difficulty level.'
        }
      ],
      hint: 'The text says "finite rules allow infinite sentence creation." What does this tell you about what "generative" means?',
      relatedVocabulary: ['vocab_3'],
      learningPoint: '"Generative" is a key linguistic concept - understanding it helps recognize language\'s creative capacity'
    },
    {
      id: 'q2',
      level: 1,
      type: 'vocabulary_context',
      difficulty: 'easy',
      paragraph: 'para_c',
      question: 'What does "variant" mean when describing the FOXP2 gene?',
      text: 'Humans possess a variant of this gene',
      options: [
        {
          id: 'q2_a',
          text: 'A different version or form of the gene',
          correct: true,
          explanation: 'Correct. "Variant" means a different version or form. Humans have a modified version of the FOXP2 gene that differs from the version found in other primates, and this human variant emerged approximately 200,000 years ago and is important for the fine motor control required for speech production.'
        },
        {
          id: 'q2_b',
          text: 'A missing gene that is not present',
          correct: false,
          explanation: '"Variant" means a different version exists, not that the gene is missing or absent. The text says humans "possess" the variant, showing it exists and is present. A variant is a modified form, not an absence.'
        },
        {
          id: 'q2_c',
          text: 'An identical copy of the same gene',
          correct: false,
          explanation: 'The text says the variant "differs from the versions found in other primates," showing it\'s different and modified, not identical. The human variant has specific changes that make it distinct from primate versions, which is why it\'s called a variant.'
        },
        {
          id: 'q2_d',
          text: 'A broken or non-functional gene',
          correct: false,
          explanation: 'The variant is functional and important - it\'s what makes human speech possible. Mutations in this gene cause problems, but the variant itself (the human version) is functional and crucial for the fine motor control required for speech production.'
        }
      ],
      hint: 'The text says the variant "differs from the versions found in other primates." What does this tell you about what "variant" means?',
      relatedVocabulary: ['vocab_9'],
      learningPoint: '"Variant" is important in genetics - understanding it helps in reading about genetic differences and evolution'
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
          text: 'Animal communication is better than human language',
          correct: false,
          explanation: 'The text describes human language as "unique" with "distinctive features" that enable complex capabilities, showing it\'s more advanced, not worse.'
        },
        {
          id: 'q3_b',
          text: 'Human language is a unique communication system with distinctive features but its evolutionary origin remains mysterious',
          correct: true,
          explanation: 'This captures the paragraph\'s main points: (1) Language origin is a mystery and one of science\'s great questions, (2) Human language is unique with distinctive features (symbolic representation, generative capacity, abstract concepts), (3) These features enabled civilization and complex thought, (4) Evolution is hard to trace because language leaves no fossil record. This covers the entire paragraph\'s purpose of introducing language as both remarkable and mysterious.'
        },
        {
          id: 'q3_c',
          text: 'Language evolution is easy to study and well-documented',
          correct: false,
          explanation: 'The text says language "leaves no fossil record" making it "difficult to trace" and describes its origin as "one of science\'s great questions," showing it\'s hard to study and not well-documented. The lack of physical evidence makes language evolution challenging to research.'
        },
        {
          id: 'q3_d',
          text: 'Only humans can communicate and exchange information',
          correct: false,
          explanation: 'The text explicitly mentions "animal communication," showing animals do communicate. Human language is unique with distinctive features (symbolic, generative, abstract), but it\'s not the only form of communication. The paragraph distinguishes human language from other communication systems, not communication itself.'
        }
      ],
      hint: 'The paragraph introduces language as a mystery, describes its unique features, shows its importance, and mentions the difficulty of studying its evolution. What is the overall message?',
      relatedVocabulary: ['vocab_1', 'vocab_2', 'vocab_3', 'vocab_4', 'vocab_5'],
      learningPoint: 'Main ideas often balance what we know (features, importance) with what we don\'t know (mystery, difficulty of study)'
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
          text: 'All researchers agree on when language evolved',
          correct: false,
          explanation: 'The text describes "various theories" and "alternative theories," showing disagreement, not agreement.'
        },
        {
          id: 'q4_b',
          text: 'Researchers propose competing theories about when language evolved with evidence supporting different views',
          correct: true,
          explanation: 'This captures the paragraph\'s themes: (1) Multiple competing theories exist about language evolution timing, (2) Sudden emergence theory (50,000-100,000 years ago) supported by archaeological evidence of symbolic artifacts, (3) Gradual evolution theory (2 million years ago) supported by primate studies showing precursor abilities, (4) Evidence from archaeology and primate studies supporting different views. This shows the ongoing debate and the evidence each theory uses.'
        },
        {
          id: 'q4_c',
          text: 'Language appeared exactly 50,000 years ago without any debate',
          correct: false,
          explanation: 'The text gives a range (50,000-100,000 years) for one theory and mentions alternative theories suggesting much earlier evolution (2 million years ago), showing significant uncertainty and ongoing debate, not exact dates or consensus. The paragraph presents competing views, not definitive answers.'
        },
        {
          id: 'q4_d',
          text: 'Only humans can learn symbols and symbolic associations',
          correct: false,
          explanation: 'The text says great apes "can learn symbolic associations" and "combine symbols," showing they have some language-related abilities and precursor capacities. While human language is unique, other primates do have some symbolic learning abilities, which is why they\'re mentioned as evidence for gradual evolution theories.'
        }
      ],
      hint: 'The paragraph presents different theories and evidence. What is the overall message about the debate?',
      relatedVocabulary: ['vocab_6', 'vocab_7', 'vocab_8'],
      learningPoint: 'Main themes often present competing theories - recognizing this helps understand scientific debates'
    },
    {
      id: 'q5',
      level: 3,
      type: 'inference',
      difficulty: 'hard',
      paragraph: 'para_b',
      question: 'Why does the author mention that great apes "possess some precursor abilities" to language?',
      options: [
        {
          id: 'q5_a',
          text: 'To show that language evolution built on existing cognitive abilities rather than appearing completely new',
          correct: true,
          explanation: 'Correct. By showing apes have language-related abilities (symbolic associations, combining symbols), the author suggests language didn\'t appear "de novo" (completely new) but evolved from existing cognitive capacities. This supports gradual evolution theories that see language developing over time from simpler communication systems, rather than appearing suddenly without precursors.'
        },
        {
          id: 'q5_b',
          text: 'To prove apes can speak and communicate exactly like humans',
          correct: false,
          explanation: 'The text says apes have "precursor abilities" - early foundations and building blocks, not full human language. They can learn symbols and combine them, but don\'t have the full generative, abstract, symbolic capacity of human language. The mention shows evolutionary continuity, not equivalence.'
        },
        {
          id: 'q5_c',
          text: 'To show language is not unique to humans and apes have full language',
          correct: false,
          explanation: 'The text describes human language as "unique" with "distinctive features" that distinguish it from animal communication. Apes have precursor abilities and some language-related capacities, but not full human language with its symbolic, generative, and abstract features. Language remains uniquely human in its complete form.'
        },
        {
          id: 'q5_d',
          text: 'To criticize primate research methods and findings',
          correct: false,
          explanation: 'The author uses primate studies as evidence to support theories about language evolution, not as criticism. The tone is informative and uses primate research to illustrate evolutionary continuity, showing how language may have built on existing abilities. The mention is supportive, not critical.'
        }
      ],
      hint: 'The text says language evolution "built upon existing cognitive capacities rather than appearing completely de novo." What does this tell you about why ape abilities are mentioned?',
      relatedVocabulary: ['vocab_7', 'vocab_8'],
      learningPoint: 'Authors use comparative evidence to support theories - here: ape abilities support gradual evolution'
    },
    {
      id: 'q6',
      level: 3,
      type: 'inference',
      difficulty: 'hard',
      paragraph: 'para_c',
      question: 'What does the author imply by saying language "has been subject to strong evolutionary selection pressures"?',
      options: [
        {
          id: 'q6_a',
          text: 'Language abilities provided significant survival advantages that evolution strongly favored',
          correct: true,
          explanation: 'Correct. "Selection pressures" means evolution actively favored language abilities because they provided significant advantages for survival and reproduction. The author shows this through specialized brain regions (Broca\'s area for speech production, Wernicke\'s area for language comprehension) - evolution created these specialized areas because language was so beneficial. This implies language was crucial for coordinating hunting, sharing resources, transmitting knowledge, and managing complex social relationships.'
        },
        {
          id: 'q6_b',
          text: 'Language was not important for human evolution and survival',
          correct: false,
          explanation: '"Strong selection pressures" means evolution actively and strongly favored language because it provided advantages, showing it was very important for human evolution and survival. The development of specialized brain regions and the fact that language became a "defining human characteristic" demonstrate its evolutionary significance.'
        },
        {
          id: 'q6_c',
          text: 'Language evolved by accident without any evolutionary purpose',
          correct: false,
          explanation: 'Selection pressures mean evolution actively favored language because it provided significant advantages, suggesting purposeful evolutionary development, not accident. The specialized brain regions and the fact that language became universal in humans show it was selected for, not accidental.'
        },
        {
          id: 'q6_d',
          text: 'Only some people have language abilities and others do not',
          correct: false,
          explanation: 'The text describes language as a "defining human characteristic," suggesting all humans have it. Selection pressures made language universal in humans, not limited to some individuals. The specialized brain regions and evolutionary selection show language became a universal human trait.'
        }
      ],
      hint: 'What does "selection pressures" mean in evolution? What happens when evolution strongly favors a trait?',
      relatedVocabulary: ['vocab_10'],
      learningPoint: '"Selection pressures" shows evolutionary importance - understanding this helps recognize when authors emphasize a trait\'s significance'
    },
    {
      id: 'q7',
      level: 4,
      type: 'synthesis',
      difficulty: 'very_hard',
      paragraph: null,
      question: 'How does the author develop the argument about language evolution across all three paragraphs?',
      options: [
        {
          id: 'q7_a',
          text: 'From mystery and unique features to competing theories and evidence to genetic insights and evolutionary advantages',
          correct: true,
          explanation: 'Perfect synthesis. Paragraph A: Establishes the mystery and language\'s unique features (symbolic, generative, abstract) that enabled civilization. Paragraph B: Presents competing theories about when/how (sudden emergence 50,000-100,000 years ago vs. gradual evolution 2 million years ago) with archaeological and primate evidence. Paragraph C: Provides genetic/neurological evidence (FOXP2 gene variant, specialized brain regions) and discusses why language evolved (social needs, practical advantages, survival benefits). This builds a comprehensive picture: what language is → when it might have evolved → why it was so important.'
        },
        {
          id: 'q7_b',
          text: 'From proven scientific facts to unproven speculative claims and theories',
          correct: false,
          explanation: 'The text presents evidence and theories throughout, not a progression from proven to unproven. It balances what we know (unique features, genetic evidence, brain regions) with what we\'re still learning (exact timing, evolutionary mechanisms). The structure is about building understanding across different aspects, not moving from certainty to uncertainty.'
        },
        {
          id: 'q7_c',
          text: 'From simple basic explanations to increasingly complex and detailed descriptions',
          correct: false,
          explanation: 'While complexity increases somewhat, the main progression is: what language is and why it\'s mysterious (A) → when/how it evolved with competing theories (B) → genetic evidence and why it evolved (C). The structure is about different aspects of language evolution, not just increasing complexity.'
        },
        {
          id: 'q7_d',
          text: 'From human language characteristics to animal communication systems and behaviors',
          correct: false,
          explanation: 'The text focuses on human language throughout all three paragraphs. Animal communication is mentioned briefly for comparison (to show precursor abilities and support gradual evolution theories), but it\'s not the main focus or progression. The argument centers on human language evolution, not animal communication.'
        }
      ],
      hint: 'Look at what each paragraph addresses: A = what language is and why it\'s mysterious, B = when/how it evolved, C = genetic evidence and why it evolved. How do these build a complete picture?',
      relatedVocabulary: ['vocab_1', 'vocab_2', 'vocab_3', 'vocab_4', 'vocab_5', 'vocab_7', 'vocab_9', 'vocab_10'],
      learningPoint: 'Effective scientific arguments often follow: definition/features → theories/evidence → mechanisms/importance - recognizing this structure helps understand complex topics'
    },
    {
      id: 'q8',
      level: 4,
      type: 'synthesis',
      difficulty: 'very_hard',
      paragraph: null,
      question: 'What is the author\'s overall argument about human language evolution?',
      options: [
        {
          id: 'q8_a',
          text: 'Human language is a unique complex system that enabled civilization with competing theories about evolution but evidence shows it was strongly selected for',
          correct: true,
          explanation: 'This captures the complete argument: (1) Language is unique with distinctive features (symbolic, generative, abstract) that distinguish it from animal communication (A), (2) Enabled civilization and complex thought (A), (3) Evolutionary origin is mysterious with competing theories about timing (sudden vs. gradual) (A, B), (4) Genetic/neurological evidence exists (FOXP2, specialized brain regions) (C), (5) Strongly selected for due to enormous survival advantages (C), (6) Defining human characteristic that fundamentally shapes how we understand the world (C). The author combines mystery with evidence, showing both what we know and what we\'re still learning.'
        },
        {
          id: 'q8_b',
          text: 'Language is not important for humans and had no role in evolution',
          correct: false,
          explanation: 'The text describes language as enabling "civilization\'s development" and being a "defining human characteristic" with "enormous advantages" that provided "significant survival advantages." It was subject to "strong evolutionary selection pressures," clearly showing its importance for human evolution and development.'
        },
        {
          id: 'q8_c',
          text: 'We know exactly when and how language evolved with complete certainty',
          correct: false,
          explanation: 'The text emphasizes the "mystery" of language origin, describes it as "one of science\'s great questions," and presents "competing theories" with different timelines (50,000-100,000 years vs. 2 million years), showing significant uncertainty about when/how, not certainty or complete understanding.'
        },
        {
          id: 'q8_d',
          text: 'Language is identical to animal communication systems and behaviors',
          correct: false,
          explanation: 'The text explicitly contrasts human language with animal communication, describing language as "unique" with "distinctive features" (symbolic representation, generative capacity, abstract concepts) that animals don\'t have. While apes have precursor abilities, human language remains uniquely human in its complete form.'
        }
      ],
      hint: 'Combine the mystery (A), the theories (B), and the evidence/importance (C). What is the author\'s overall message about language evolution?',
      relatedVocabulary: ['vocab_1', 'vocab_2', 'vocab_3', 'vocab_4', 'vocab_5', 'vocab_7', 'vocab_9', 'vocab_10'],
      learningPoint: 'Overall arguments in scientific texts often balance mystery with evidence - here: unique system with uncertain origins but clear importance and evolutionary significance'
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

