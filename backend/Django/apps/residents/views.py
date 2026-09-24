"""
Views for Residents module.
"""
import csv
import io

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Resident
from .serializers import (
    ResidentSerializer,
    ResidentCreateSerializer,
    ResidentUpdateSerializer
)


class ResidentListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list all residents and create new residents.
    """
    queryset = Resident.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'purok_zone', 'sms_enabled']
    search_fields = ['full_name', 'mobile_number', 'address', 'purok_zone']
    ordering_fields = ['full_name', 'purok_zone', 'created_at']
    ordering = ['purok_zone', 'full_name']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ResidentCreateSerializer
        return ResidentSerializer

    def perform_create(self, serializer):
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='create',
            entity='resident',
            details=serializer.validated_data
        )
        serializer.save()


class ResidentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update or delete a resident.
    """
    queryset = Resident.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'resident_id'
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ResidentUpdateSerializer
        return ResidentSerializer
    
    def perform_update(self, serializer):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='update',
            entity='resident',
            entity_id=str(self.get_object().resident_id),
            details=serializer.validated_data
        )
        serializer.save()
    
    def perform_destroy(self, instance):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='delete',
            entity='resident',
            entity_id=str(instance.resident_id),
            details={'full_name': instance.full_name}
        )
        instance.delete()


class ResidentCreateView(generics.CreateAPIView):
    """
    API endpoint to create a new resident.
    """
    queryset = Resident.objects.all()
    serializer_class = ResidentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='create',
            entity='resident',
            details=serializer.validated_data
        )
        serializer.save()


class ResidentImportView(APIView):
    """
    API endpoint to import residents from a CSV file.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response({'detail': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        if not csv_file.name.endswith('.csv'):
            return Response({'detail': 'Invalid file type. Please upload a CSV file.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_file = csv_file.read().decode('utf-8')
        except Exception:
            return Response({'detail': 'Unable to read CSV file.'}, status=status.HTTP_400_BAD_REQUEST)

        reader = csv.DictReader(io.StringIO(decoded_file))
        required_fields = ['full_name', 'mobile_number', 'address', 'purok_zone', 'status', 'sms_enabled']
        if not all(field in reader.fieldnames for field in required_fields):
            return Response(
                {'detail': f'CSV file must contain the following columns: {", ".join(required_fields)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        created = []
        errors = []

        for row_index, row in enumerate(reader, start=2):
            row_data = {key: (value or '').strip() for key, value in row.items()}
            sms_enabled_value = row_data.get('sms_enabled', '').lower()
            if sms_enabled_value in ['true', '1', 'yes', 'y']:
                row_data['sms_enabled'] = True
            elif sms_enabled_value in ['false', '0', 'no', 'n']:
                row_data['sms_enabled'] = False
            else:
                row_data['sms_enabled'] = True

            serializer = ResidentCreateSerializer(data=row_data)
            if serializer.is_valid():
                resident = serializer.save()
                created.append(ResidentSerializer(resident).data)
            else:
                errors.append({'row': row_index, 'errors': serializer.errors})

        status_code = status.HTTP_201_CREATED if not errors else status.HTTP_207_MULTI_STATUS
        return Response({'created': created, 'errors': errors}, status=status_code)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def active_residents_view(request):
    """
    API endpoint to get all active residents with SMS enabled.
    Used for SMS alert sending.
    """
    residents = Resident.objects.filter(
        status='active',
        sms_enabled=True
    ).order_by('purok_zone', 'full_name')
    
    serializer = ResidentSerializer(residents, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def residents_by_purok_view(request, purok_zone):
    """
    API endpoint to get residents by purok/zone.
    """
    residents = Resident.objects.filter(
        purok_zone=purok_zone
    ).order_by('full_name')
    
    serializer = ResidentSerializer(residents, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def resident_statistics_view(request):
    """
    API endpoint to get resident statistics.
    """
    total_residents = Resident.objects.count()
    active_residents = Resident.objects.filter(status='active').count()
    sms_enabled = Resident.objects.filter(sms_enabled=True).count()
    
    # Count by purok
    purok_counts = {}
    for resident in Resident.objects.values('purok_zone'):
        purok = resident['purok_zone']
        purok_counts[purok] = purok_counts.get(purok, 0) + 1
    
    # Count by status
    status_counts = {}
    for status_choice in Resident.STATUS_CHOICES:
        status_name = status_choice[0]
        count = Resident.objects.filter(status=status_name).count()
        status_counts[status_name] = count
    
    data = {
        'total_residents': total_residents,
        'active_residents': active_residents,
        'sms_enabled_count': sms_enabled,
        'purok_counts': purok_counts,
        'status_counts': status_counts
    }
    
    return Response(data)
