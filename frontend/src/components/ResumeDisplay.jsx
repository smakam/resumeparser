import React, { useState } from 'react'
import './ResumeDisplay.css'

const MODEL_LABELS = {
  'openai:gpt-4o': 'GPT-4o',
  'openai:gpt-5-preview': 'GPT-5 Preview',
  'gemini:gemini-1.5-pro-latest': 'Gemini 1.5 Pro',
  'gemini:gemini-3-pro-preview': 'Gemini 3 Pro Preview',
  'huggingface:deepseek-ai/DeepSeek-R1-Distill-Llama-70B:groq': 'DeepSeek R1 (Groq)',
  'huggingface:openai/gpt-oss-120b': 'GPT-OSS-120B'
}

function ResumeDisplay({ data }) {
  const [activeTab, setActiveTab] = useState('contact')
  const results = data?.results || []
  const errors = data?.errors || []
  const hasResults = results.length > 0

  const exportToJSON = () => {
    const jsonStr = JSON.stringify(data, null, 2)
    const blob = new Blob([jsonStr], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'resume-data.json'
    a.click()
    URL.revokeObjectURL(url)
  }

  const exportToCSV = () => {
    if (!hasResults) return
    let csv = 'Model,Field,Value\n'
    
    results.forEach((result) => {
      const key = `${result.provider}:${result.model_name}`
      const label = MODEL_LABELS[key] || result.model_name
      const resume = result.resume || {}
      const contact = resume.contact_info || {}

      csv += `${label},Name,${contact.name || ''}\n`
      csv += `${label},Email,${contact.email || ''}\n`
      csv += `${label},Phone,${contact.phone || ''}\n`
      csv += `${label},City,${contact.city || ''}\n`
      csv += `${label},TotalExperienceYears,${resume.total_experience_years || ''}\n`
      if (resume.skills && resume.skills.length > 0) {
        csv += `${label},Skills,"${resume.skills.map((s) => s.name).join('; ')}"\n`
      }
    })
    
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'resume-data.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  const renderModelHeader = (result) => {
    const key = `${result.provider}:${result.model_name}`
    const label = MODEL_LABELS[key] || result.model_name
    const providerLabel = result.inference_provider
      ? `${result.provider.toUpperCase()} (${result.inference_provider})`
      : result.provider.toUpperCase()
    return (
      <div className="model-panel-header">
        <div>
          <span className="model-name">{label}</span>
          <span className="model-provider">{providerLabel}</span>
        </div>
        <div className="model-metrics">
          {typeof result.api_latency_ms === 'number' && (
            <span className="metric-badge">Model: {result.api_latency_ms} ms</span>
          )}
          {typeof result.latency_ms === 'number' && (
            <span className="metric-badge">Total: {result.latency_ms} ms</span>
          )}
          {typeof result.confidence === 'number' && (
            <span className="metric-badge metric-confidence">
              {(result.confidence * 100).toFixed(1)}% confidence
            </span>
          )}
          {typeof result.cost_usd === 'number' && (
            <span className="metric-badge">~${result.cost_usd.toFixed(4)}</span>
          )}
        </div>
      </div>
    )
  }

  const renderPanels = (renderFn) => (
    <div className="model-panels">
      {results.map((result) => (
        <div key={`${result.provider}:${result.model_name}`} className="model-panel">
          {renderModelHeader(result)}
          {renderFn(result.resume || {})}
        </div>
      ))}
    </div>
  )

  // if (!hasResults) {
  //   return null
  // }

  return (
    <div className="resume-display">
      <div className="display-header">
        <div>
          <h2>Parsed Resume Data</h2>
          <p className="subtitle">
            Comparing {results.length} model{results.length > 1 ? 's' : ''}{' '}
            {results.length > 0 &&
              `(providers: ${results
                .map((r) => `${r.provider}${r.inference_provider ? `/${r.inference_provider}` : ''}`)
                .join(', ')})`}
          </p>
        </div>
        <div className="export-buttons">
          <button onClick={exportToJSON} className="export-btn">Export JSON</button>
          <button onClick={exportToCSV} className="export-btn">Export CSV</button>
        </div>
      </div>

      {errors && errors.length > 0 && (
        <div className="warning-message">
          <strong>Some models failed:</strong>
          <ul>
            {errors.map((err, idx) => (
              <li key={idx}>
                {err.provider ? `${err.provider}:${err.model_name}` : 'Unknown'} - {err.message}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="tabs">
        {['contact', 'experience', 'education', 'skills', 'other'].map((tab) => (
          <button
            key={tab}
            className={activeTab === tab ? 'active' : ''}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      <div className="tab-content">
        {activeTab === 'contact' && (
          <div className="section">
            <h3>Contact & Summary</h3>
            {renderPanels((resume) => {
              const contact = resume.contact_info || {}
              return (
                <>
                  <div className="info-grid">
                    <div className="info-item">
                      <strong>Name:</strong> {contact.name || 'N/A'}
                    </div>
                    <div className="info-item">
                      <strong>Email:</strong> {contact.email || 'N/A'}
                    </div>
                    <div className="info-item">
                      <strong>Phone:</strong> {contact.phone || 'N/A'}
                    </div>
                    <div className="info-item">
                      <strong>City:</strong> {contact.city || 'N/A'}
                    </div>
                    <div className="info-item">
                      <strong>Total Experience:</strong>{' '}
                      {resume.total_experience_years
                        ? `${resume.total_experience_years} yrs${resume.total_experience_months ? ` ${resume.total_experience_months} mos` : ''}`
                        : 'N/A'}
                    </div>
                  </div>
                  {(resume.summary || resume.objective) && (
                    <div className="summary-section">
                      {resume.summary && (
                        <div>
                          <strong>Summary:</strong>
                          <p>{resume.summary}</p>
                        </div>
                      )}
                      {resume.objective && (
                        <div>
                          <strong>Objective:</strong>
                          <p>{resume.objective}</p>
                        </div>
                      )}
                    </div>
                  )}
                </>
              )
            })}
          </div>
        )}

        {activeTab === 'experience' && (
          <div className="section">
            <h3>Work Experience</h3>
            {renderPanels((resume) => (
              resume.experience && resume.experience.length > 0 ? (
                <div className="experience-list">
                  {resume.experience.map((exp, idx) => (
                    <div key={idx} className="experience-item">
                      <div className="experience-header">
                        <h4>{exp.position || 'N/A'}</h4>
                        <span className="company">{exp.company || 'N/A'}</span>
                      </div>
                      <div className="experience-dates">
                        {exp.start_date || 'N/A'} - {exp.is_current ? 'Present' : (exp.end_date || 'N/A')}
                      </div>
                      {exp.summary && <p className="experience-summary">{exp.summary}</p>}
                      {exp.achievements && exp.achievements.length > 0 && (
                        <ul className="achievements-list">
                          {exp.achievements.map((ach, i) => (
                            <li key={i}>{ach}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="no-data">No experience data found</p>
              )
            ))}
          </div>
        )}

        {activeTab === 'education' && (
          <div className="section">
            <h3>Education</h3>
            {renderPanels((resume) => (
              resume.education && resume.education.length > 0 ? (
                <div className="education-list">
                  {resume.education.map((edu, idx) => (
                    <div key={idx} className="education-item">
                      <h4>{edu.degree || 'N/A'}</h4>
                      {edu.field_of_study && <p className="field">{edu.field_of_study}</p>}
                      <p className="institution">{edu.institution || 'N/A'}</p>
                      <div className="education-details">
                        {edu.graduation_year && <span>Graduated: {edu.graduation_year}</span>}
                        {edu.gpa && <span>GPA: {edu.gpa}</span>}
                        {edu.location && <span>{edu.location}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="no-data">No education data found</p>
              )
            ))}
          </div>
        )}

        {activeTab === 'skills' && (
          <div className="section">
            <h3>Skills & Languages</h3>
            {renderPanels((resume) => (
              <>
                {resume.skills && resume.skills.length > 0 ? (
                  <div className="skills-grid">
                    {resume.skills.map((skill, idx) => (
                      <div key={idx} className="skill-item">
                        <span className="skill-name">{skill.name}</span>
                        {skill.category && <span className="skill-category">{skill.category}</span>}
                        {skill.proficiency && <span className="skill-proficiency">{skill.proficiency}</span>}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="no-data">No skills data found</p>
                )}
                {resume.languages && resume.languages.length > 0 && (
                  <div className="languages-section">
                    <h4>Languages</h4>
                    <div className="languages-list">
                      {resume.languages.map((lang, idx) => (
                        <span key={idx} className="language-tag">{lang}</span>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ))}
          </div>
        )}

        {activeTab === 'other' && (
          <div className="section">
            <h3>Certifications, Projects & More</h3>
            {renderPanels((resume) => (
              <>
                {resume.certifications && resume.certifications.length > 0 && (
                  <div className="subsection">
                    <h4>Certifications</h4>
                    <ul className="info-list">
                      {resume.certifications.map((cert, idx) => (
                        <li key={idx}>
                          <strong>{cert.name || 'N/A'}</strong>
                          {cert.issuer && <span> - {cert.issuer}</span>}
                          {cert.issue_date && <span> ({cert.issue_date})</span>}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {resume.projects && resume.projects.length > 0 && (
                  <div className="subsection">
                    <h4>Projects</h4>
                    <div className="projects-list">
                      {resume.projects.map((project, idx) => (
                        <div key={idx} className="project-item">
                          <h5>{project.name || 'N/A'}</h5>
                          {project.description && <p>{project.description}</p>}
                          {project.technologies && project.technologies.length > 0 && (
                            <div className="tech-tags">
                              {project.technologies.map((tech, i) => (
                                <span key={i} className="tech-tag">{tech}</span>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {resume.awards && resume.awards.length > 0 && (
                  <div className="subsection">
                    <h4>Awards</h4>
                    <ul className="info-list">
                      {resume.awards.map((award, idx) => (
                        <li key={idx}>
                          <strong>{award.title || 'N/A'}</strong>
                          {award.issuer && <span> - {award.issuer}</span>}
                          {award.date && <span> ({award.date})</span>}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {resume.patents && resume.patents.length > 0 && (
                  <div className="subsection">
                    <h4>Patents</h4>
                    <ul className="info-list">
                      {resume.patents.map((patent, idx) => (
                        <li key={idx}>
                          <strong>{patent.title || 'N/A'}</strong>
                          {patent.patent_number && <span> - {patent.patent_number}</span>}
                          {patent.issue_date && <span> ({patent.issue_date})</span>}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {resume.references && resume.references.length > 0 && (
                  <div className="subsection">
                    <h4>References</h4>
                    <ul className="info-list">
                      {resume.references.map((ref, idx) => (
                        <li key={idx}>{ref}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {(!resume.certifications || resume.certifications.length === 0) &&
                 (!resume.projects || resume.projects.length === 0) &&
                 (!resume.awards || resume.awards.length === 0) &&
                 (!resume.patents || resume.patents.length === 0) &&
                 (!resume.references || resume.references.length === 0) && (
                  <p className="no-data">No additional information found</p>
                )}
              </>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ResumeDisplay
