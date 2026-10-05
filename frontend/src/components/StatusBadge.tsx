import type { PublicationStatus } from '../types'
export default function StatusBadge({status}:{status:PublicationStatus}){ return <span className={`status status-${status}`}>{status.replaceAll('_',' ')}</span> }
