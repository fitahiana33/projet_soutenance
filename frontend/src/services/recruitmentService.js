/**
 * recruitmentService.js - Service layer for Recruitment & Talent API calls
 */
import api from './api'

const recruitmentService = {
  getOverview() {
    return api.get('/recruitment/overview')
  },

  getJobs() {
    return api.get('/recruitment/jobs')
  },

  getJobOffers() {
    return api.get('/recruitment/jobs')
  },

  createJob(payload) {
    return api.post('/recruitment/jobs', payload)
  },

  createJobOffer(payload) {
    return api.post('/recruitment/jobs', payload)
  },

  updateJobOffer(id, payload) {
    return api.put(`/recruitment/jobs/${id}`, payload)
  },

  updateJobStatus(id, status) {
    return api.put(`/recruitment/jobs/${id}/status?status=${status}`)
  },

  deleteJobOffer(id) {
    return api.delete(`/recruitment/jobs/${id}`)
  },

  updateCandidateStatus(id, status) {
    return api.put(`/recruitment/candidates/${id}/status?status=${status}`)
  },

  getCandidates() {
    return api.get('/recruitment/candidates')
  },

  createCandidate(payload) {
    return api.post('/recruitment/candidates', payload)
  },

  /**
   * Match candidates to a job offer using the scoring engine
   * @param {{ job_id: number, top_n?: number }} payload
   */
  matchCandidates(payload) {
    return api.post('/recruitment/match', payload)
  },

  runMatch(payload) {
    return api.post('/recruitment/match', payload)
  }
}

export default recruitmentService
