import { RiMindMap } from '@remixicon/react'
import { useTranslation } from 'react-i18next'
import { useDocLink } from '@/context/i18n'

const FailBranchCard = () => {
  const { t } = useTranslation()
  const docLink = useDocLink()

  return (
    <div className='px-4 pt-2'>
      <div className='rounded-[10px] bg-workflow-process-bg p-4'>
        <div className='mb-2 flex h-8 w-8 items-center justify-center rounded-[10px] border-[0.5px] border-components-card-border bg-components-card-bg shadow-lg'>
          <RiMindMap className='h-5 w-5 text-text-tertiary' />
        </div>
        <div className='system-sm-medium mb-1 text-text-secondary'>
          {t('workflow.nodes.common.errorHandle.failBranch.customize')}
        </div>
        <div className='system-xs-regular text-text-tertiary'>
          {t('workflow.nodes.common.errorHandle.failBranch.customizeTip')}
          &nbsp;
          <a
            href={docLink('/guides/workflow/error-handling/error-type')}
            target='_blank'
            className='text-text-accent'
          >
            {t('workflow.common.learnMore')}
          </a>
        </div>
      </div>
    </div>
  )
}

export default FailBranchCard
