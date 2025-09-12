// Mock API service for realistic fact-checking responses
class MockApiService {
  constructor() {
    this.factCheckDatabase = {
      'vaccine_autism': {
        verdict: 'false',
        confidence: 95,
        explanation: 'Extensive scientific research has consistently shown no link between vaccines and autism. Multiple large-scale studies involving millions of children have found no causal relationship. The original study claiming this link was retracted due to fraudulent data.',
        sources: [
          {
            id: 1,
            title: 'CDC - Vaccine Safety',
            url: 'https://www.cdc.gov/vaccinesafety/',
            organization: 'CDC'
          },
          {
            id: 2,
            title: 'WHO - Vaccines and Autism',
            url: 'https://www.who.int/news-room/feature-stories/detail/autism-spectrum-disorders',
            organization: 'WHO'
          },
          {
            id: 3,
            title: 'Lancet Retraction of Wakefield Study',
            url: 'https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(97)11096-0/fulltext',
            organization: 'The Lancet'
          }
        ]
      },
      'climate_change': {
        verdict: 'true',
        confidence: 98,
        explanation: 'Climate change is supported by overwhelming scientific consensus. 97% of actively publishing climate scientists agree that human activities are the primary cause of recent climate change. Multiple lines of evidence from temperature records, ice cores, and satellite data confirm this.',
        sources: [
          {
            id: 1,
            title: 'IPCC Climate Report 2023',
            url: 'https://www.ipcc.ch/',
            organization: 'IPCC'
          },
          {
            id: 2,
            title: 'NASA Climate Evidence',
            url: 'https://climate.nasa.gov/evidence/',
            organization: 'NASA'
          },
          {
            id: 3,
            title: 'Scientific Consensus on Climate Change',
            url: 'https://climate.nasa.gov/scientific-consensus/',
            organization: 'NASA'
          }
        ]
      },
      'covid_microchip': {
        verdict: 'false',
        confidence: 99,
        explanation: 'COVID-19 vaccines do not contain microchips or tracking devices. This conspiracy theory has been thoroughly debunked by medical authorities worldwide. Vaccines contain mRNA or viral proteins to help build immunity, not electronic devices.',
        sources: [
          {
            id: 1,
            title: 'Reuters Fact Check: RFID microchips in vaccines',
            url: 'https://www.reuters.com/article/uk-factcheck-coronavirus-vaccine-microc-idUSKBN21032X',
            organization: 'Reuters'
          },
          {
            id: 2,
            title: 'WHO - Coronavirus disease (COVID-19) advice',
            url: 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public/myth-busters',
            organization: 'WHO'
          }
        ]
      },
      '5g_covid': {
        verdict: 'false',
        confidence: 97,
        explanation: '5G networks do not cause COVID-19. The virus spreads through respiratory droplets, not radio waves. Many countries without 5G networks have had COVID-19 outbreaks, proving there is no connection.',
        sources: [
          {
            id: 1,
            title: 'WHO - 5G mobile networks and health',
            url: 'https://www.who.int/news-room/fact-sheets/detail/electromagnetic-fields-and-public-health-mobile-phones',
            organization: 'WHO'
          },
          {
            id: 2,
            title: 'BBC Reality Check: 5G and coronavirus',
            url: 'https://www.bbc.com/news/52168096',
            organization: 'BBC'
          }
        ]
      }
    }
  }

  async factCheck(claim, image = null) {
    // Simulate API processing time
    await this.delay(1500 + Math.random() * 1000)

    // Classify the claim
    const claimType = this.classifyClaim(claim)
    
    if (claimType in this.factCheckDatabase) {
      const result = { ...this.factCheckDatabase[claimType] }
      result.processing_time = 1.5 + Math.random() * 1.0
      return result
    } else {
      // Generate a contextual response based on keywords
      return this.generateContextualResponse(claim)
    }
  }

  classifyClaim(claim) {
    const lowerClaim = claim.toLowerCase()
    
    if ((lowerClaim.includes('vaccine') || lowerClaim.includes('vaccination')) && 
        lowerClaim.includes('autism')) {
      return 'vaccine_autism'
    } else if (lowerClaim.includes('climate') && 
               (lowerClaim.includes('change') || lowerClaim.includes('warming') || 
                lowerClaim.includes('hoax'))) {
      return 'climate_change'
    } else if ((lowerClaim.includes('covid') || lowerClaim.includes('coronavirus')) && 
               (lowerClaim.includes('microchip') || lowerClaim.includes('chip') || 
                lowerClaim.includes('tracking'))) {
      return 'covid_microchip'
    } else if (lowerClaim.includes('5g') && 
               (lowerClaim.includes('covid') || lowerClaim.includes('coronavirus'))) {
      return '5g_covid'
    } else {
      return 'unknown'
    }
  }

  generateContextualResponse(claim) {
    const lowerClaim = claim.toLowerCase()
    
    // Health-related claims
    if (lowerClaim.includes('vaccine') || lowerClaim.includes('health') || 
        lowerClaim.includes('medicine')) {
      return {
        verdict: 'uncertain',
        confidence: 65,
        explanation: 'I need more specific information about this health claim to provide a definitive fact-check. For medical information, please consult with healthcare professionals and trusted medical organizations.',
        sources: [
          {
            id: 1,
            title: 'WHO - Health Topics',
            url: 'https://www.who.int/health-topics/',
            organization: 'WHO'
          },
          {
            id: 2,
            title: 'CDC - Health Information',
            url: 'https://www.cdc.gov/',
            organization: 'CDC'
          }
        ],
        processing_time: 1.2
      }
    }
    
    // Political claims
    else if (lowerClaim.includes('election') || lowerClaim.includes('political') || 
             lowerClaim.includes('government')) {
      return {
        verdict: 'uncertain',
        confidence: 60,
        explanation: 'Political claims require careful verification with multiple sources. Please check with official government sources and established fact-checking organizations for accurate information.',
        sources: [
          {
            id: 1,
            title: 'PolitiFact',
            url: 'https://www.politifact.com/',
            organization: 'PolitiFact'
          },
          {
            id: 2,
            title: 'FactCheck.org',
            url: 'https://www.factcheck.org/',
            organization: 'FactCheck.org'
          }
        ],
        processing_time: 1.8
      }
    }
    
    // Science-related claims
    else if (lowerClaim.includes('science') || lowerClaim.includes('research') || 
             lowerClaim.includes('study')) {
      return {
        verdict: 'uncertain',
        confidence: 70,
        explanation: 'Scientific claims should be verified against peer-reviewed research and established scientific consensus. Please provide more specific details for accurate fact-checking.',
        sources: [
          {
            id: 1,
            title: 'National Academy of Sciences',
            url: 'https://www.nationalacademies.org/',
            organization: 'NAS'
          },
          {
            id: 2,
            title: 'Scientific American - Fact Check',
            url: 'https://www.scientificamerican.com/',
            organization: 'Scientific American'
          }
        ],
        processing_time: 1.6
      }
    }
    
    // Default response
    else {
      return {
        verdict: 'uncertain',
        confidence: 55,
        explanation: 'I need more specific information to provide a definitive fact-check. Could you please rephrase your claim or provide more context? I work best with specific, factual statements.',
        sources: [
          {
            id: 1,
            title: 'Snopes - Fact Checking',
            url: 'https://www.snopes.com/',
            organization: 'Snopes'
          },
          {
            id: 2,
            title: 'AllSides - Balanced News',
            url: 'https://www.allsides.com/',
            organization: 'AllSides'
          }
        ],
        processing_time: 1.0
      }
    }
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

export default new MockApiService()
