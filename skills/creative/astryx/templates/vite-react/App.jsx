import React, { useState } from 'react'

// Import Astryx components
import { Button } from '@astryxdesign/core/Button'
import { Card } from '@astryxdesign/core/Card'
import { Heading } from '@astryxdesign/core/Heading'
import { Text } from '@astryxdesign/core/Text'
import { Badge } from '@astryxdesign/core/Badge'
import { TextInput } from '@astryxdesign/core/TextInput'
import { Switch } from '@astryxdesign/core/Switch'
import { Slider } from '@astryxdesign/core/Slider'
import { ProgressBar } from '@astryxdesign/core/ProgressBar'
import { Avatar } from '@astryxdesign/core/Avatar'
import { AvatarGroup } from '@astryxdesign/core/AvatarGroup'
import { HStack } from '@astryxdesign/core/HStack'
import { VStack } from '@astryxdesign/core/VStack'
import { Divider } from '@astryxdesign/core/Divider'
import { Skeleton } from '@astryxdesign/core/Skeleton'
import { Spinner } from '@astryxdesign/core/Spinner'
import { Tooltip } from '@astryxdesign/core/Tooltip'
import { StatusDot } from '@astryxdesign/core/StatusDot'

export default function App() {
  const [darkMode, setDarkMode] = useState(false)
  const [sliderValue, setSliderValue] = useState(50)

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <HStack justifyContent="space-between" alignItems="center" marginBottom="2rem">
        <VStack gap="0.5rem">
          <Heading level={1}>Astryx Demo</Heading>
          <Text color="muted">Meta's open-source component library</Text>
        </VStack>
        <HStack gap="1rem">
          <Switch checked={darkMode} onChange={() => setDarkMode(!darkMode)} />
          <Text size="sm">{darkMode ? 'Dark' : 'Light'}</Text>
        </HStack>
      </HStack>

      <Divider marginBottom="2rem" />

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        <Card>
          <Heading level={3}>Buttons</Heading>
          <VStack gap="1rem" marginTop="1rem">
            <HStack gap="0.5rem">
              <Button variant="primary">Primary</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="tertiary">Tertiary</Button>
            </HStack>
            <HStack gap="0.5rem">
              <Button size="sm">Small</Button>
              <Button size="md">Medium</Button>
              <Button size="lg">Large</Button>
            </HStack>
          </VStack>
        </Card>

        <Card>
          <Heading level={3}>Form Controls</Heading>
          <VStack gap="1rem" marginTop="1rem">
            <TextInput placeholder="Enter text..." />
            <Slider value={sliderValue} onChange={setSliderValue} min={0} max={100} />
            <Text size="sm">Value: {sliderValue}</Text>
            <ProgressBar value={sliderValue} />
          </VStack>
        </Card>

        <Card>
          <Heading level={3}>Status</Heading>
          <VStack gap="1rem" marginTop="1rem">
            <HStack gap="1rem">
              <Badge variant="success">Success</Badge>
              <Badge variant="warning">Warning</Badge>
              <Badge variant="error">Error</Badge>
            </HStack>
            <HStack gap="1rem">
              <StatusDot status="online" /> <Text>Online</Text>
              <StatusDot status="away" /> <Text>Away</Text>
            </HStack>
          </VStack>
        </Card>

        <Card>
          <Heading level={3}>Avatars</Heading>
          <VStack gap="1rem" marginTop="1rem">
            <HStack gap="1rem">
              <Avatar name="John" size="sm" />
              <Avatar name="Jane" size="md" />
              <Avatar name="Bob" size="lg" />
            </HStack>
            <AvatarGroup max={3}>
              <Avatar name="A" /><Avatar name="B" /><Avatar name="C" /><Avatar name="D" />
            </AvatarGroup>
          </VStack>
        </Card>
      </div>
    </div>
  )
}
